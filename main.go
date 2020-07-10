package main

import (
	"context"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"

	"github.com/gorilla/mux"
	"github.com/jackc/pgx"
)

type DBClient struct {
	db *pgx.Conn
}

type HTMLData struct {
	Platform []string
}

type Game struct {
	Name     string
	Year     int
	Platform string
	Rating   int
}

type DBAnswer struct {
	Games []Game
}

//QueryHandler ...
func (driver *DBClient) QueryHandler(w http.ResponseWriter, r *http.Request) {
	queryParams := r.URL.Query()
	w.WriteHeader(http.StatusOK)
	queryPattern := "select * from games_list "
	amountOfQueries := 0
	for _, value := range queryParams {
		if strings.Join(value, "") != "" {
			amountOfQueries++
		}
	}
	var needsOrdering bool = false
	if strings.Join(queryParams["order by"], "") != "" {
		needsOrdering = true
		amountOfQueries--
	}
	orderBy := ""
	if amountOfQueries != 0 {
		queryPattern = strings.Join([]string{queryPattern, " where "}, "")
		currentQuery := 1
		for query, value := range queryParams {
			valueString := strings.Join(value, "")
			if valueString == "" {
				continue
			}
			if query == "platform" {
				queryPattern = strings.Join([]string{queryPattern, "platform = ", "'", valueString, "' "}, "")
			} else if query == "order by" {
				orderBy = strings.Join([]string{orderBy, "order by ", valueString}, "")
				continue
			} else {
				queryPattern = strings.Join([]string{queryPattern, query, " > ", valueString, " "}, "")
			}
			if currentQuery < amountOfQueries {
				queryPattern = strings.Join([]string{queryPattern, " and "}, "")
			}
			currentQuery++
		}
		if !needsOrdering {
			queryPattern = strings.Join([]string{queryPattern, ";"}, "")
		}
	}
	if needsOrdering {
		queryPattern = strings.Join([]string{queryPattern, strings.Join([]string{"order by ", strings.Join(queryParams["order by"], "")}, "")}, "")
		queryPattern = strings.Join([]string{queryPattern, ";"}, "")
	}
	fmt.Println(queryPattern)
	rows, err := driver.db.Query(context.Background(), queryPattern)
	if err != nil {
		fmt.Fprintf(w, err.Error())
	}
	defer rows.Close()
	var answer DBAnswer
	for rows.Next() {
		var name, platform string
		var year, rating, id int
		err := rows.Scan(&id, &name, &rating, &year, &platform)
		if err != nil {
			fmt.Fprintf(w, err.Error())
		}
		game := Game{
			Name:     name,
			Year:     year,
			Platform: platform,
			Rating:   rating}
		answer.Games = append(answer.Games, game)
	}
	template, err := template.ParseFiles("templates/dbanswer.html")
	if err != nil {
		fmt.Println(err.Error())
	}
	template.Execute(w, answer)
}

//LoadMainPage ...
func (driver *DBClient) LoadMainPage(w http.ResponseWriter, r *http.Request) {
	rows, err := driver.db.Query(context.Background(), "select distinct platform from games_list;")
	if err != nil {
		fmt.Fprintf(w, err.Error())
	}
	defer rows.Close()
	var Platform []string
	for rows.Next() {
		var platform string
		err := rows.Scan(&platform)
		if err != nil {
			fmt.Fprintf(w, err.Error())
		}
		Platform = append(Platform, platform)
	}
	data := HTMLData{Platform: Platform}
	template, err := template.ParseFiles("templates/mainpage.html")
	if err != nil {
		fmt.Println(err.Error())
	}
	template.Execute(w, data)
}

func main() {
	r := mux.NewRouter()
	db, err := pgx.Connect(context.Background(), "postgres://qelderdelta:lolxd322@localhost/qelderdelta")
	defer db.Close(context.Background())
	client := &DBClient{db: db}
	if err != nil {
		fmt.Println(err.Error())
	}
	r.HandleFunc("/", client.LoadMainPage)
	r.HandleFunc("/games", client.QueryHandler)
	r.PathPrefix("/styles/").Handler(http.StripPrefix("/styles/", http.FileServer(http.Dir("templates/styles/"))))
	r.Queries("rating", "year", "platform", "order by")
	if err := http.ListenAndServe(":8888", r); err != nil {
		log.Fatal(err)
	}
}
