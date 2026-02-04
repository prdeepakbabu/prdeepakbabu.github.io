---
title: "Market Basket Analysis/Association Rule Mining using R package – arules"
date: "2010-11-13"
canonical: "https://prdeepakbabu.wordpress.com/2010/11/13/market-basket-analysisassociation-rule-mining-using-r-package-arules/"
source: "wordpress"
---
<p>In my <a href="https://prdeepakbabu.wordpress.com/2010/02/24/association-rule-mining/" target="_blank">previous post</a>, i had discussed about Association rule mining in some detail.  Here i have shown the implementation of the concept using open source tool <a href="http://www.r-project.org/" target="_blank">R</a> using the package arules. Market Basket Analysis is a specific application of Association rule mining, where retail transaction baskets are analysed to find the products which are likely to be purchased together. The analysis output forms the input for  recomendation engines/marketing strategies. <span id="more-154"></span>Association rule mining cannot be done using Base SAS/ Enterprise Guide and hence R seems to be the best option in my opinion.<br />
The arules package has Apriori algorithm which i will be demonstrating here using a sample transaction file called &#8220;Transactions_sample.csv&#8221;( find below)</p>
<p><span style="text-decoration:underline;"><strong>R Source Code:</strong></span></p>
<p>#To set the working directory to folder where source files are placed.(set this to directory as per your needs)<br />
<span style="color:brown;">setwd(&#8220;C:/Documents and Settings/deepak.babu/Desktop/output&#8221;);</span></p>
<p><span style="color:green;">#Install the R package arules</span><br />
<span style="color:brown;">install.packages(&#8220;arules&#8221;);</span></p>
<p><span style="color:green;">#load the arules package</span><br />
<span style="color:brown;">library(&#8220;arules&#8221;);</span></p>
<p><span style="color:green;"># read the transaction file as a Transaction class<br />
# file &#8211; csv/txt<br />
# format &#8211; single/basket (For ‘basket’ format, each line in the transaction data file represents a transaction<br />
#           where the items (item labels) are separated by the characters specified by sep. For ‘single’ format,<br />
#           each line corresponds to a single item, containing at least ids for the transaction and the item. )<br />
# rm.duplicates &#8211; TRUE/FALSE<br />
# cols &#8211;   For the ‘single’ format, cols is a numeric vector of length two giving the numbers of the columns (fields)<br />
#           with the transaction and item ids, respectively. For the ‘basket’ format, cols can be a numeric scalar<br />
#           giving the number of the column (field) with the transaction ids. If cols = NULL<br />
# sep &#8211; &#8220;,&#8221; for csv, &#8220;\t&#8221; for tab delimited</span><br />
<span style="color:brown;">txn = read.transactions(file=&#8221;Transactions_sample.csv&#8221;, rm.duplicates= FALSE, format=&#8221;single&#8221;,sep=&#8221;,&#8221;,cols =c(1,2));</span></p>
<p><span style="color:green;"># Run the apriori algorithm</span><br />
<span style="color:brown;">basket_rules &lt;- apriori(txn,parameter = list(sup = 0.5, conf = 0.9,target=&#8221;rules&#8221;));</span></p>
<p><span style="color:green;"># Check the generated rules using inspect</span><br />
<span style="color:brown;">inspect(basket_rules);</span></p>
<p><span style="color:green;">#If huge number of rules are generated specific rules can read using index</span><br />
<span style="color:brown;">inspect(basket_rules[1]);</span></p>
<p><span style="color:blue;"> </span></p>
<p><span style="color:green;">#############################################################################<br />
##############  SUPPLEMENTARY  INFO  ########################################<br />
#############################################################################<br />
#To visualize the item frequency in txn file</span><br />
<span style="color:brown;">itemFrequencyPlot(txn);</span></p>
<p><span style="color:green;">#To see how the transaction file is read into txn variable.</span><br />
<span style="color:brown;">inspect(txn);</span></p>
<p><strong><span style="text-decoration:underline;"><span style="color:black;">Output:<br />
</span></span></strong><br />
<span style="color:blue;"><br />
parameter specification:<br />
confidence minval smax arem  aval originalSupport support minlen maxlen target<br />
0.9    0.1    1 none FALSE            TRUE     0.5      1      5  rules<br />
ext<br />
FALSE<br />
algorithmic control:<br />
filter tree heap memopt load sort verbose<br />
0.1 TRUE TRUE  FALSE TRUE    2    TRUE</span></p>
<p><span style="color:blue;">apriori &#8211; find association rules with the apriori algorithm<br />
version 4.21 (2004.05.09)        (c) 1996-2004   Christian Borgelt<br />
set item appearances &#8230;[0 item(s)] done [0.00s].<br />
set transactions &#8230;[6 item(s), 7 transaction(s)] done [0.00s].<br />
sorting and recoding items &#8230; [2 item(s)] done [0.00s].<br />
creating transaction tree &#8230; done [0.00s].<br />
checking subsets of size 1 2 done [0.00s].<br />
writing &#8230; [1 rule(s)] done [0.00s].<br />
creating S4 object  &#8230; done [0.00s].</span></p>
<p><span style="color:black;"><br />
As we see from the output, Number of rules generated are 1, with support = 50% and confidence = 90%. The generated rules can be checked using inspect(basket_rules) command:<br />
<span style="color:blue;">lhs                              rhs            support               confidence     lift<br />
1 {Choclates} =&gt; {Pencil}  0.5714286          1                        1.166667</span></span></p>
<p><span style="color:black;"><span style="color:black;">The above rule means &#8220;If a chocolate is brought then there is 90% likelihood of purchase of pencil&#8221;. The support 0.57 indicates that 57% of the transaction in the data involve chocolate purchases.  The confidence of 90% indicates out of the transactions which involve chocolates, 90% of them also involved purchase of pencils. Hence the support indicates goodness of the choice of rule and confidence indicates the correctness of the rule.</span></span></p>
<p>Also we can see the distribution of items within transactions using image(txn) and  itemFrequencyPlot(txn).</p>
<p>Transaction.csv<br />
===========<br />
1001,Choclates<br />
1001,Pencil<br />
1001,Marker<br />
1002,Pencil<br />
1002,Choclates<br />
1003,Pencil<br />
1003,Coke<br />
1003,Eraser<br />
1004,Pencil<br />
1004,Choclates<br />
1004,Cookies<br />
1005,Marker<br />
1006,Pencil<br />
1006,Marker<br />
1007,Pencil<br />
1007,Choclates</p>
<p><strong><a href="https://prdeepakbabu.wordpress.com/2010/02/24/association-rule-mining/">Prev</a>        </strong>                                                                                                                                                                               <a href="https://prdeepakbabu.wordpress.com/2012/05/26/clustering-techniques/"> </a><strong><a href="https://prdeepakbabu.wordpress.com/2012/05/26/clustering-techniques/">Next</a><a href="https://prdeepakbabu.wordpress.com/2010/11/13/market-basket-analysisassociation-rule-mining-using-r-package-arules/"><br />
</a></strong><strong><a href="https://prdeepakbabu.wordpress.com/2010/02/24/association-rule-mining/">Related: Association Rule Mining Overview</a>                                           <a href="https://prdeepakbabu.wordpress.com/2012/05/26/clustering-techniques/">Related: Clustering Techniques Overview<br />
</a></strong><strong><a href="https://prdeepakbabu.wordpress.com/2010/02/24/association-rule-mining/">(Market Basket Analysis)</a>                                                                                                        </strong></p>
<p><strong>Recommended Posts:</strong><br />
<strong><a href="https://prdeepakbabu.wordpress.com/2012/03/06/big-data-hadoop-map-reduce/">Big Data: Hadoop Map Reduce &#8211; what is it all about?<br />
</a><a href="https://prdeepakbabu.wordpress.com/2011/10/25/location-intelligence-using-social-media-data-customer-location-aware-systems/">Location Intelligene &#8211; Customer Location Aware Systems</a></strong></p>
<div data-shortcode="caption" id="attachment_171" style="width: 310px" class="wp-caption alignleft"><a href="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg"><img aria-describedby="caption-attachment-171" data-attachment-id="171" data-permalink="https://prdeepakbabu.wordpress.com/2010/11/13/market-basket-analysisassociation-rule-mining-using-r-package-arules/freqplot/" data-orig-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg" data-orig-size="672,672" data-comments-opened="1" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;}" data-image-title="Item Frequency Plot" data-image-description="" data-image-caption="&lt;p&gt;Item Frequency Plot&lt;/p&gt;
" data-medium-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg?w=300" data-large-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg?w=545" class="size-medium wp-image-171" title="Item Frequency Plot" src="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg?w=300&#038;h=300" alt="" width="300" height="300" srcset="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg?w=300 300w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg?w=600 600w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/freqplot.jpeg?w=150 150w" sizes="(max-width: 300px) 100vw, 300px" /></a><p id="caption-attachment-171" class="wp-caption-text">Item Frequency Plot</p></div>
<div data-shortcode="caption" id="attachment_177" style="width: 310px" class="wp-caption alignleft"><a href="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg"><img aria-describedby="caption-attachment-177" loading="lazy" data-attachment-id="177" data-permalink="https://prdeepakbabu.wordpress.com/2010/11/13/market-basket-analysisassociation-rule-mining-using-r-package-arules/imageplot/" data-orig-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg" data-orig-size="672,672" data-comments-opened="1" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;}" data-image-title="imageplot" data-image-description="&lt;p&gt;Image(txn) showing density &lt;/p&gt;
" data-image-caption="&lt;p&gt;Image(txn) showing density &lt;/p&gt;
" data-medium-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg?w=300" data-large-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg?w=545" class="size-medium wp-image-177" title="imageplot" src="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg?w=300&#038;h=300" alt="Image(txn) showing density " width="300" height="300" srcset="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg?w=300 300w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg?w=600 600w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/11/imageplot.jpeg?w=150 150w" sizes="(max-width: 300px) 100vw, 300px" /></a><p id="caption-attachment-177" class="wp-caption-text">Image(txn) showing density</p></div>