{
	"settings": {
		"analysis": {
			"analyzer": {
				"optimizeIK": {
					"type": "custom",
					"tokenizer": "ik_max_word",
					"filter": [
					"stemmer"
					]
				}
			}
		}
	},
	"mappings": {
		"properties": {
			"name": {
				"type": "text",
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
			},
			"mechanism": {
				"type": "text",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_max_word"
			},
			"paper": {
				"properties": {
					"source_journal":{
						"properties": {
							"date": {
								"type": "text"
							}
						}		
					}
				}
			}
		}
	}
}