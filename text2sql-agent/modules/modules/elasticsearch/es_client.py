import logging
import urllib3
from elasticsearch import Elasticsearch
from configs import Config
from typing import List, Dict, Optional
import json
import warnings

# Disable InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticSearchClient():
    def __init__(self) -> None:
        self.hosts = Config.ElasticsearchConf.HOST
        self.USERNAME = Config.ElasticsearchConf.USERNAME
        self.PASSWORD = Config.ElasticsearchConf.PASSWORD
        self.verify_certs = False

    def es(self) -> Elasticsearch:
        """Initialize and return an Elasticsearch client."""
        return Elasticsearch(
            hosts=self.hosts,
            basic_auth=(self.USERNAME, self.PASSWORD),
            verify_certs=self.verify_certs
        )

    def index_document_production(self, index_name, question, sql, use_keyword, upvote_count, downvote_count) -> bool:
        """Index a document in Elasticsearch to Production."""
        try:
            es = self.es()

            document = {
                "question": question,
                "sql": sql,
                "use_keyword": use_keyword,
                "upvote_count": upvote_count,
                "downvote_count": downvote_count,
            }
            es.index(index=index_name, body=document)
            logger.info(f"Document indexed to production successfully")
            return True
        except Exception as e:
            logger.error(f"Error indexing document: {e}", exc_info=True)
            return False
        
    def index_document_staging(self, index_name, question, sql, sql_score, use_keyword, upvote_count, downvote_count) -> bool:
        """Index a document in Elasticsearch to Staging."""
        try:
            es = self.es()

            document = {
                "question": question,
                "sql": sql,
                "sql_score": sql_score,
                "use_keyword": use_keyword,
                "upvote_count": upvote_count,
                "downvote_count": downvote_count,
            }
            es.index(index=index_name, body=document)
            logger.info(f"Document indexed to staging successfully")
            return True
        except Exception as e:
            logger.error(f"Error indexing document: {e}", exc_info=True)
            return False
    
    def search_document(self, index_name, query, use_keyword, minimum_should_match="1<-1 5<75% 9<70% 14<60%") -> Optional[dict]:
        """Search for documents in Elasticsearch and return the top result."""
        try:    
            es = self.es()
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "match": {
                                "question": {
                                    "query": query,
                                    "analyzer": "standard",
                                    "minimum_should_match": minimum_should_match,
                                }
                            }
                        },
                        "filter": {
                            "term": {
                                "use_keyword": use_keyword
                            }
                        }
                    }
                }
            }
            result = es.search(index=index_name, body=body, size=1)  # Ensure only the top result is returned
            document_match_count = result['hits']['total']['value']
            if result and document_match_count > 0:
                logger.info(f"Search successful in index: {index_name}, query: {query}")
                return result['hits']['hits'][0]  # Return only the top result
            else:
                logger.info(f"No matching documents found in index: {index_name} for query: {query}")
                return None
        except Exception as e:
            logger.error(f"Error searching documents: {e}", exc_info=True)
            return None
        

    def update_document(self, index_name, doc_id, question, sql_query, use_keyword) -> bool:
        """Update a document in Elasticsearch."""
        try:
            es = self.es()
            document = {
                "question": question,
                "sql_query": sql_query,
                "use_keyword": use_keyword,
            }
            es.update(index=index_name, id=doc_id, body={"doc": document})
            logger.info(f"Document updated successfully in index: {index_name}, id: {doc_id}")
            return True 
        except Exception as e:
            logger.error(f"Error updating document: {e}", exc_info=True)
            return False
    
    def delete_document(self, index_name, doc_id) -> bool:
        """Delete a document from Elasticsearch."""
        try:
            es = self.es()
            es.delete(index=index_name, id=doc_id)
            logger.info(f"Document deleted successfully from index: {index_name}, id: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}", exc_info=True)
            return False