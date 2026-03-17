# Drill Test Gadget

## dns api page 

    ```bash go run api/dns_api.go
    curl "http://localhost:8080/api/dns-fuzz?domain=yildiz.edu.tr&url=https://yildiz.edu.tr/&wordlist=utils/ss.txt&fs_filter=-1&status_filter=-1&threads=20" 
    ````


## directory api


go run dir_fuzz.go https://yildiz.edu.tr ss.txt -1 -1 20