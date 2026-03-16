package directory_api

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

type Result struct {
	Path     string `json:"path"`
	Status   int    `json:"status"`
	Length   int64  `json:"length"`
	BodyHash string `json:"body_hash"`
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

func directoryFuzz(baseURL string, wordlist []string, fsFilter int64, statusFilter int, threads int) []Result {
	refLen, refHash := getBodyHash(baseURL)
	fmt.Printf("[*] Reference body length: %d, hash: %s\n", refLen, refHash)

	pathChan := make(chan string, threads)
	resultChan := make(chan Result, threads)
	var wg sync.WaitGroup
	results := []Result{}

	worker := func() {
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

	// Start workers
	for i := 0; i < threads; i++ {
		wg.Add(1)
		go worker()
	}

	// Send paths to workers
	go func() {
		for _, path := range wordlist {
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
		results = append(results, res)
	}
	return results
}

func ApiHandler(w http.ResponseWriter, r *http.Request) {
	// Parametreleri al
	baseURL := r.URL.Query().Get("base_url")
	wordlistFile := r.URL.Query().Get("wordlist")
	fsFilterStr := r.URL.Query().Get("fs_filter")
	statusFilterStr := r.URL.Query().Get("status_filter")
	threadsStr := r.URL.Query().Get("threads")

	if baseURL == "" || wordlistFile == "" {
		http.Error(w, "base_url and wordlist required", http.StatusBadRequest)
		return
	}

	fsFilter := int64(-1)
	statusFilter := -1
	threads := 10

	if fsFilterStr != "" {
		fsFilter, _ = strconv.ParseInt(fsFilterStr, 10, 64)
	}
	if statusFilterStr != "" {
		statusFilter, _ = strconv.Atoi(statusFilterStr)
	}
	if threadsStr != "" {
		threads, _ = strconv.Atoi(threadsStr)
	}

	// Wordlist dosyasını oku
	data, err := os.ReadFile(wordlistFile)
	if err != nil {
		http.Error(w, "Wordlist file not found", http.StatusBadRequest)
		return
	}
	wordlist := strings.Split(string(data), "\n")

	// Fuzz işlemini başlat
	results := directoryFuzz(baseURL, wordlist, fsFilter, statusFilter, threads)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(results)
}

func main() {
	http.HandleFunc("/api/directory-fuzz", ApiHandler)
	fmt.Println("API server running on :8080")
	http.ListenAndServe(":8080", nil)
}
