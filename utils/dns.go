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
	Vhost    string
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

func worker(domain, url string, fsFilter int64, statusFilter int, refHash string, vhostChan <-chan string, resultChan chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	client := &http.Client{Timeout: 5 * time.Second}
	for vhost := range vhostChan {
		hostHeader := fmt.Sprintf("%s.%s", vhost, domain)
		req, err := http.NewRequest("GET", url, nil)
		if err != nil {
			continue
		}
		req.Header.Set("Host", hostHeader)
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
			// Sadece hash ana domain'den farklıysa göster
			if hash != refHash {
				resultChan <- Result{hostHeader, resp.StatusCode, length, hash}
			}
		}
	}
}

func main() {
	if len(os.Args) < 5 {
		fmt.Println("Usage: vhost_fuzz <DOMAIN> <WORDLIST> <URL> <FS_Filter> [Status_Filter] [Threads]")
		os.Exit(1)
	}

	domain := os.Args[1]
	wordlist := os.Args[2]
	url := os.Args[3]
	fsFilter, _ := strconv.ParseInt(os.Args[4], 10, 64)
	statusFilter := -1
	threads := 10

	if len(os.Args) > 5 {
		statusFilter, _ = strconv.Atoi(os.Args[5])
	}
	if len(os.Args) > 6 {
		threads, _ = strconv.Atoi(os.Args[6])
	}

	// Referans ana domain yanıtının hash'ini al
	refLen, refHash := getBodyHash(url)
	fmt.Printf("[*] Reference body length: %d, hash: %s\n", refLen, refHash)

	file, err := os.Open(wordlist)
	if err != nil {
		fmt.Printf("Error opening wordlist: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	vhostChan := make(chan string, threads)
	resultChan := make(chan Result, threads)
	var wg sync.WaitGroup

	// Start workers
	for i := 0; i < threads; i++ {
		wg.Add(1)
		go worker(domain, url, fsFilter, statusFilter, refHash, vhostChan, resultChan, &wg)
	}

	// Read wordlist and send to workers
	go func() {
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			vhost := scanner.Text()
			if vhost != "" {
				vhostChan <- vhost
			}
		}
		close(vhostChan)
	}()

	// Collect results
	go func() {
		wg.Wait()
		close(resultChan)
	}()

	for res := range resultChan {
		fmt.Printf("[+] %s - Status: %d - Length: %d - Hash: %s\n", res.Vhost, res.Status, res.Length, res.BodyHash)
	}
}
