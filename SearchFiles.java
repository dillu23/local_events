
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Date;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

/** Simple command-line based search demo. */
public class SearchFiles {

  private SearchFiles() {}

  /** Simple command-line based search demo. */
  public static void main(String[] args) throws Exception {
    String usage =
      "Usage:\tjava org.apache.lucene.demo.SearchFiles [-index dir] [-field f] [-repeat n] [-queries file] [-query string] [-raw] [-paging hitsPerPage]\n\nSee http://lucene.apache.org/core/4_1_0/demo/ for details.";
    if (args.length > 0 && ("-h".equals(args[0]) || "-help".equals(args[0]))) {
      System.out.println(usage);
      System.exit(0);
    }

    String index = args[0];
    String field = "contents";
    String queries = null;
    int repeat = 0;
    boolean raw = true;
    String queryString = args[1];
    int hitsPerPage = 5;
    
    IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(index)));
    IndexSearcher searcher = new IndexSearcher(reader);
    // :Post-Release-Update-Version.LUCENE_XY:
    Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_48);

    // :Post-Release-Update-Version.LUCENE_XY:
    QueryParser parser = new QueryParser(Version.LUCENE_48, field, analyzer);
    Query query = parser.parse(queryString);
    doPagingSearch(searcher, query, hitsPerPage, raw);
    reader.close();
  }

  /**
   * This demonstrates a typical paging search scenario, where the search engine presents 
   * pages of size n to the user. The user can then go to the next page if interested in
   * the next hits.
   * 
   * When the query is executed for the first time, then only enough results are collected
   * to fill 5 result pages. If the user wants to page beyond this limit, then the query
   * is executed another time and all hits are collected.
   * 
   */
  public static void doPagingSearch(IndexSearcher searcher, Query query, 
                                     int hitsPerPage, boolean raw) throws IOException {
 
    // Collect enough docs to show 5 pages
    //TopDocs results = searcher.search(query, 5 * hitsPerPage);
    TopDocs results = searcher.search(query, 5);
    ScoreDoc[] hits = results.scoreDocs;
    
    int numTotalHits = results.totalHits;
    //System.out.println(numTotalHits + " total matching documents");

    int start = 0;
    int end = Math.min(numTotalHits, hitsPerPage);
    for (int i = start; i < end; i++) {
      /*if (raw) {                              // output raw format
        System.out.println("doc="+hits[i].doc+" score="+hits[i].score);
      }*/

      Document doc = searcher.doc(hits[i].doc);
      String path = doc.get("path");
      if (path != null) {
        //System.out.println((i+1) + ". " + path);
        System.out.println(path + "\t" + hits[i].score);
        //String title = doc.get("title");
        /*if (title != null) {
          //System.out.println("   Title: " + doc.get("title"));
          System.out.println(doc.get("title") + "\t" + hits[i].score);
        }*/
      } else {
        System.out.println((i+1) + ". " + "No path for this document");
      }
                
    }
  }
}