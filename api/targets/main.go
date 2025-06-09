package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strings"
	"sync"

	"github.com/google/uuid"
)

type Target struct {
	ID        string `json:"id"`
	Domain    string `json:"domain"`
	Program   string `json:"program"`
	Status    string `json:"status"`
	LastScan  string `json:"lastScan"`
	VulnCount int    `json:"vulnCount"`
}

var (
	targets = []Target{
		{
			ID:        uuid.New().String(),
			Domain:    "example.com",
			Program:   "Example Program",
			Status:    "active",
			LastScan:  "2024-06-09",
			VulnCount: 3,
		},
		{
			ID:        uuid.New().String(),
			Domain:    "test.org",
			Program:   "Test Program",
			Status:    "paused",
			LastScan:  "2024-06-08",
			VulnCount: 1,
		},
	}
	mutex sync.Mutex
)

func main() {
	http.HandleFunc("/api/targets", targetsHandler)
	http.HandleFunc("/api/targets/", targetByIDHandler)
	log.Println("Listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

// /api/targets (GET, POST)
func targetsHandler(w http.ResponseWriter, r *http.Request) {
	mutex.Lock()
	defer mutex.Unlock()

	if r.Method == http.MethodGet {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(targets)
		return
	}

	if r.Method == http.MethodPost {
		var req struct {
			Domain  string `json:"domain"`
			Program string `json:"program"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}
		if req.Domain == "" || req.Program == "" {
			http.Error(w, "Domain and program are required", http.StatusBadRequest)
			return
		}
		newTarget := Target{
			ID:        uuid.New().String(),
			Domain:    req.Domain,
			Program:   req.Program,
			Status:    "active",
			LastScan:  "",
			VulnCount: 0,
		}
		targets = append(targets, newTarget)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(newTarget)
		return
	}

	http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
}

// /api/targets/{id} (PATCH, DELETE)
func targetByIDHandler(w http.ResponseWriter, r *http.Request) {
	mutex.Lock()
	defer mutex.Unlock()

	id := strings.TrimPrefix(r.URL.Path, "/api/targets/")
	index := -1
	for i, t := range targets {
		if t.ID == id {
			index = i
			break
		}
	}
	if index == -1 {
		http.Error(w, "Target not found", http.StatusNotFound)
		return
	}

	switch r.Method {
	case http.MethodPatch:
		var req struct {
			Status string `json:"status"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request", http.StatusBadRequest)
			return
		}
		if req.Status != "" {
			targets[index].Status = req.Status
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(targets[index])
	case http.MethodDelete:
		targets = append(targets[:index], targets[index+1:]...)
		w.WriteHeader(http.StatusNoContent)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}
