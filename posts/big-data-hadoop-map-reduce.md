---
title: "Big Data: Hadoop Map Reduce"
date: "2012-03-05"
canonical: "https://prdeepakbabu.wordpress.com/2012/03/06/big-data-hadoop-map-reduce/"
source: "wordpress"
---
<p>Hadoop is an open source framework for writing and running distributed application that process huge amounts of data ( more famously called Big Data). The name Hadoop is not an acronym; it’s a made-up name. The project’s creator, Doug Cutting, explains how the name came about: <em>“The name my kid gave a stuffed yellow elephant. Short, relatively easy to spell and pronounce, meaningless, and not used elsewhere: those are my naming criteria. Kids are good at generating such. Googol is a kid’s term”</em></p>
<p>It has two components</p>
<p>&#8211;          Distributed Storage ( uses HDFS – Hadoop file system)<br />
Ensures the data is distributed evenly across all the nodes of Hadoop cluster. There is option of replicate data across nodes (redundancy) to provide capabilities to recover from failures.</p>
<p>&#8211;          Distributed Computing ( uses MR – Map Reduce Paradigm)<br />
Once the data is available on Hadoop cluster. The MR codes ( typically return in Java,C++) is moved to each of the nodes for computation on the data. Map Reduce has two phases mapper and Reducer.</p>
<p>One of the early examples of a distributed computing include SETI@home project, where a group of people volunteered to offer CPU time of their personal computer for research on radio telescope data to find intelligent life outside earth. However this differs from Hadoop MR is in the fact that, data is moved to place where computing takes place in case SETI, while code is moved to the place of data in latter case. Other projects include finding the largest prime numbers, sorting Pet bytess of data in shortest time,etc.</p>
<p>Applications of Hadoop MR – Big data</p>
<ul>
<li>          Weblog analysis</li>
<li>          Fraud detection</li>
<li>          Text Mining</li>
<li>          Search Engine Indexing</li>
<li>          LinkedIn uses for “Who viewed  your profile” and “People you may know – recommendations”</li>
<li>          Amazon.com uses for book recommendation</li>
</ul>
<p>Hadoop MR Wrapper applications include</p>
<ul>
<li>          Pig : A data flow language and execution environment for exploring very large datasets. Pig runs on HDFS and MapReduce clusters.</li>
<li>          Hive : A distributed data warehouse. Hive manages data stored in HDFS and provides a query language based on SQL (and which is translated by the<br />
runtime engine to MapReduce jobs) for querying the data.</li>
<li>          Mahout : Machine Learning implementation in Map Reduce.</li>
</ul>