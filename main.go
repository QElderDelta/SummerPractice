package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"

	"github.com/gorilla/mux"
	"github.com/jackc/pgx"
)

type DBClient struct {
	db *pgx.Conn
}

//QueryHandler ...
func (driver *DBClient) QueryHandler(w http.ResponseWriter, r *http.Request) {
	queryParams := r.URL.Query()
	w.WriteHeader(http.StatusOK)
	queryPattern := "select * from games_list"
	amountOfQueries := len(queryParams)
	if amountOfQueries != 0 {
		queryPattern = strings.Join([]string{queryPattern, " where "}, "")
		currentQuery := 1
		for query, value := range queryParams {
			valueString := strings.Join(value, "")
			if query == "platform" {
				queryPattern = strings.Join([]string{queryPattern, "platform = ", "'", valueString, "' "}, "")
			} else {
				queryPattern = strings.Join([]string{queryPattern, query, " > ", valueString, " "}, "")
			}
			if currentQuery != amountOfQueries {
				queryPattern = strings.Join([]string{queryPattern, " and "}, "")
			}
			currentQuery++
		}
		queryPattern = strings.Join([]string{queryPattern, ";"}, "")
	}
	fmt.Println(queryPattern)
	rows, err := driver.db.Query(context.Background(), queryPattern)
	if err != nil {
		fmt.Fprintf(w, err.Error())
	}
	defer rows.Close()
	for rows.Next() {
		var name, platform string
		var year, rating, id int
		err := rows.Scan(&id, &name, &rating, &year, &platform)
		if err != nil {
			fmt.Fprintf(w, err.Error())
		}
		fmt.Fprintf(w, strings.Join([]string{name, strconv.Itoa(rating),
			strconv.Itoa(year), platform, "\n"}, " "))
	}
}

func main() {
	r := mux.NewRouter()
	db, err := pgx.Connect(context.Background(), "postgres://qelderdelta:lolxd322@localhost/qelderdelta")
	defer db.Close(context.Background())
	client := &DBClient{db: db}
	if err != nil {
		fmt.Println(err.Error())
	}
	r.HandleFunc("/games", client.QueryHandler)
	r.Queries("rating", "year", "platform")
	if err := http.ListenAndServe(":9000", r); err != nil {
		log.Fatal(err)
	}
}
