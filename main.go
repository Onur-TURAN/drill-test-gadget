package main

import (
	"drill-test-gadget/api/directory_api"
	"drill-test-gadget/api/dns_api"
	"fmt"
	"net/http"
)

// directoryFuzz, dnsFuzz, getBodyHash ve Result struct'larını buraya ekle
func directoryApiHandler(w http.ResponseWriter, r *http.Request) {
	directory_api.ApiHandler(w, r)
}

func dnsApiHandler(w http.ResponseWriter, r *http.Request) {
	dns_api.ApiHandler(w, r)
}

func main() {
	http.HandleFunc("/api/directory_api", directoryApiHandler)
	http.HandleFunc("/api/dns_api", dnsApiHandler)
	fmt.Println("API server running on :8080")
	http.ListenAndServe(":8080", nil)
}
