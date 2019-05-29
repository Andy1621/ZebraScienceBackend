// scholar_index
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
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
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

// organization_index
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
			"mechanism": {
				"type": "text",
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
			},
			"introduction": {
				"type": "text",
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
			}
		}
	}
}

// paper_index
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
			"astract": {
				"type": "text",
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
			},
			"author": {
				"type": "text",
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
			},
			"keyword": {
				"type": "text",
				"analyzer": "optimizeIK",
				"search_analyzer": "optimizeIK"
			},
			"source_journal":{
				"properties": {
					"date": {
						"type": "text"
					},
					"name": {
						"type": "text",
						"analyzer": "optimizeIK",
						"search_analyzer": "optimizeIK"
					}
				}		
			}
		}
	}
}