package main

import (
	"bufio"
	"crypto/sha256"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

type Result struct {
	Path     string
	Status   int
	Length   int64
	BodyHash string
}

func getBodyHash(url string) (int64, string) {
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return -1, ""
	}
	defer resp.Body.Close()
	bodyBytes, _ := io.ReadAll(resp.Body)
	hash := fmt.Sprintf("%x", sha256.Sum256(bodyBytes))
	return int64(len(bodyBytes)), hash
}

func worker(baseURL string, fsFilter int64, statusFilter int, refHash string, pathChan <-chan string, resultChan chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	client := &http.Client{Timeout: 5 * time.Second}
	for path := range pathChan {
		targetURL := fmt.Sprintf("%s/%s", baseURL, path)
		req, err := http.NewRequest("GET", targetURL, nil)
		if err != nil {
			continue
		}
		req.Header.Set("User-Agent", "biyik")

		resp, err := client.Do(req)
		if err != nil {
			continue
		}
		bodyBytes, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		length := int64(len(bodyBytes))
		hash := fmt.Sprintf("%x", sha256.Sum256(bodyBytes))

		if (fsFilter == -1 || length == fsFilter) && (statusFilter == -1 || resp.StatusCode == statusFilter) {
			if hash != refHash {
				resultChan <- Result{targetURL, resp.StatusCode, length, hash}
			}
		}
	}
}

func Directory() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: dir_fuzz <BASE_URL> <WORDLIST> <FS_Filter> [Status_Filter] [Threads]")
		os.Exit(1)
	}

	baseURL := os.Args[1]
	wordlist := os.Args[2]
	fsFilter, _ := strconv.ParseInt(os.Args[3], 10, 64)
	statusFilter := -1
	threads := 10

	if len(os.Args) > 4 {
		statusFilter, _ = strconv.Atoi(os.Args[4])
	}
	if len(os.Args) > 5 {
		threads, _ = strconv.Atoi(os.Args[5])
	}

	// Referans ana sayfa yanıtının hash'ini al
	refLen, refHash := getBodyHash(baseURL)
	fmt.Printf("[*] Reference body length: %d, hash: %s\n", refLen, refHash)

	file, err := os.Open(wordlist)
	if err != nil {
		fmt.Printf("Error opening wordlist: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	pathChan := make(chan string, threads)
	resultChan := make(chan Result, threads)
	var wg sync.WaitGroup

	// Start workers
	for i := 0; i < threads; i++ {
		wg.Add(1)
		go worker(baseURL, fsFilter, statusFilter, refHash, pathChan, resultChan, &wg)
	}

	// Read wordlist and send to workers
	go func() {
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			path := scanner.Text()
			if path != "" {
				pathChan <- path
			}
		}
		close(pathChan)
	}()

	// Collect results
	go func() {
		wg.Wait()
		close(resultChan)
	}()

	for res := range resultChan {
		fmt.Printf("[+] %s - Status: %d - Length: %d - Hash: %s\n", res.Path, res.Status, res.Length, res.BodyHash)
	}
}
