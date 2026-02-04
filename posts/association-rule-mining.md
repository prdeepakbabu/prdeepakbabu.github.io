---
title: "Association Rule Mining"
date: "2010-02-24"
canonical: "https://prdeepakbabu.wordpress.com/2010/02/24/association-rule-mining/"
source: "wordpress"
---
<p><span style="text-decoration:underline;">Association Rule Mining </span><a href="https://prdeepakbabu.wordpress.com/2010/11/13/market-basket-analysisassociation-rule-mining-using-r-package-arules/" target="_blank">[ Implementation using R here]</a><span style="text-decoration:underline;"><br />
</span></p>
<p>Association Rule mining is one of the classical DM technique. Association Rule mining is a very powerful technique of analysing / finding patterns in the data set. It is a supervised learning technique in the sense that we feed the Association Algorithm with a training data set( as called Experience E in machine learning context) to formulate hypothesis(H) . The input data to a association rule mining algorithm requires a format which will be detailed shortly.<br />
Ok let me first introduce the readers with some of the application areas of this DM technique and motivation for the study of Association analysis. The classic application of the association rule mining is to analyse the Market Basket Data of a retail store. For example, Retail stores like Wal-Mart, Reliance fresh, big bazaar gather data about customer purchase behaviour and they have complete details of the goods purchased as part of a single bill. This is called Market basket data and its analysis is termed “market basket analysis”.<span id="more-101"></span> It has been found that customers who buy diapers are more likely to buy beer. This is a pattern discovered by association analysis. Other applications include but not limited to scientific data analysis (earth science to study ocean, land and atm. Processes) and in the field of bioinformatics (genome sequence mining, etc.) Also it is used in document analysis for determining the words that often occur together and weblog mining temporal data for any pattern in online behaviour and website navigation. There are numerous other examples of association analysis which is only bounded by human imagination and capability.<br />
Let’s start with Association mining with market basket data as the example. An itemset is the group of items. A k-itemset indicates the no. of items under study is K numbers. As part of a transaction (purchase by customer) one or more items from the itemset may be included. The occurrence/purchase of an item is indicated by a value 1 while non-inclusion is indicated by a value 0. Hence a typical market basket data like the one below:</p>
<table border="1" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td valign="top"></td>
<td valign="top">Book</td>
<td valign="top">Pen</td>
<td valign="top">Pencil</td>
<td valign="top">Eraser</td>
<td valign="top">Sharpener</td>
<td valign="top">Crayons</td>
<td valign="top">Maps</td>
<td valign="top">A4 sheets</td>
</tr>
<tr>
<td valign="top">T1</td>
<td valign="top">1</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">1</td>
</tr>
<tr>
<td valign="top">T2</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">0</td>
</tr>
<tr>
<td valign="top">T3</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">1</td>
<td valign="top">0</td>
<td valign="top">0</td>
</tr>
</tbody>
</table>
<p>Hence it means<br />
T1 – {Book,Pen,Eraser,Crayons}<br />
T2 – {Pen,Eraser,Crayons}<br />
T3 – {Book,Eraer,Crayons}<br />
In the above example, we call it an 8-itemset.</p>
<p>If you see the above representation of market basket data, one may think there are few additional info which are missing like the quantity purchased, Amount involved in the transactions/purchase. Of course, the association analysis can be extended to involve such detail.<br />
The application of Association rule mining algorithm results in the discovery of rules/patterns of the following form:<br />
{Pencil} &#8211; &gt; {Eraser}<br />
{Book,Maps}- &gt; {Pen}<br />
What it simply says is “If a customer bought a pencil he is more likely to buy an eraser”. Mathematically, it says “Purchase of Pencil implies purchase of eraser”. Once a pattern is discovered, it can used/integrated into decision support system to form strategies based on the rule. In the above case, the company may use this rule to do cross-selling i.e place pencil and eraser as close to each other which increases the sales and hence profit. Just imagine, if a number of such strong rules are disovered in a jewellery shop it would result in tremendous value. Now let me answer what “strong” rule means?<br />
Now that we have defined what a rule is, we are posed with two important questions. Are all rules discovered by my algorithm is really useful / meaningful? How confident i am about the rule? To answer these questions, we use some mathematical measure to quantify the usefulness and confidence.<br />
Most common evaluation measures for a rule are support and confidence measures. There are other measures namely lift, interest factor, correlation. We will talk about it a bit later. A support measure answers the first question, the interestingness measure. It is represented in percentage. It defines how many of my transactions support this rule. If it is say 4/100 it means just 4 out of 100 transactions involve this rule, then probably this is uninteresting so we may choose to ignore it. Hence our Association rule mining algorithm sets some threshold/min value for the support to eliminate uninteresting rules and retain the interesting ones. An example of uninteresting rule could be {pen} &#8211; &gt; {eraser}, this could be an uninteresting rule as pen and eraser might be purchased as a matter of chance, i.e it has lower support.<br />
Now having answered the interestingness criteria, we are left with determining the confidence of the rule. A confidence measure quantifies the confidence as a ratio of no. of transaction holding this rule valid against the no. of transactions involving this rule. Higher the value, more reliable is the rule. A strong rule indicates a rule with higher confidence value.</p>
<p>Lets quickly jump into details of the algorithm. The Association rule mining is carried out using the famous Apriori Algorithm. We will also talk about the variations of this algorithm to apply it for continous data and hierarchial data. Before that, let’s formalize the definition of the association analysis problem:<br />
<em> “Given a set of transactions, the problem is to find all rules/patterns with support &gt;= minsup and confidence &gt;= minconf”</em></p>
<p>The Apriori Algorithm:<br />
A brute force approach is very expensive task. Hence the approach followed by apriori algorithm is to break up the requirement of computing support and confidence as a two separate tasks. In the first step, frequent itemsets are generated i.e those itemsets which holds the criteria of minimum support. In the second and final step, Rule generation is made possible by evaluation the confidence measure. Let’s visualize the approach diagrammatically as shown below:</p>
<div data-shortcode="caption" id="attachment_105" style="width: 310px" class="wp-caption alignleft"><a href="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg"><img aria-describedby="caption-attachment-105" loading="lazy" data-attachment-id="105" data-permalink="https://prdeepakbabu.wordpress.com/2010/02/24/association-rule-mining/apriori/" data-orig-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg" data-orig-size="882,396" data-comments-opened="1" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;}" data-image-title="Apriori Algorithm" data-image-description="" data-image-caption="&lt;p&gt;Apriori Algorithm&lt;/p&gt;
" data-medium-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg?w=300" data-large-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg?w=545" class="size-medium wp-image-105" title="Apriori Algorithm" src="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg?w=300&#038;h=134" alt="" width="300" height="134" srcset="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg?w=300 300w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg?w=600 600w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/apriori.jpg?w=150 150w" sizes="(max-width: 300px) 100vw, 300px" /></a><p id="caption-attachment-105" class="wp-caption-text">Apriori Algorithm</p></div>
<p>Measures could be classified into two categories – subjective and objective. A subjective measure often involves some heuristics and involves domain expertise to eliminate un interesting rules while objective measure are domain independent measures. Support and confidence are good examples of objective measures. Objective measures could be either symmetric binary or asymmetric binary. The choice of measure depends on the type of application and it must be carefully chosen to get quality results.<br />
Simpson’s paradox states that there is a possibility of misinterpretation due to the hidden variable not as part of the analysis influencing the rules/patterns.</p>
<p>The apriori algorithm can be extended to solving various other problems by making little modifications to the data representation methods, Data structures and algorithm.</p>
<ol>
<li>To handle categorital and continous data. For example gender is categorical attribute and can be represented using two items namely gender=’M’ and gender = ‘F’.</li>
<li>To handle concept of hierarchy in itemsets. For example, if IPod, Smartphone are two specific itemsets, then we can define a hierarchy item called electronic goods as a parent item.</li>
<li>To handle sequential pattern mining. Example: weblog mining, genome sequence mining, customer purchase behaviour.</li>
<li>Graph and sub-graph mining: eample – weblogs to identify navigation patterns, chemical structure analysis.</li>
<li>To identify infrequent patterns, negatively correlated patterns, etc.</li>
</ol>
<p>You can also download a copy of the above material here: <a href="https://prdeepakbabu.wordpress.com/wp-content/uploads/2010/02/association-rule-mining.pdf">Association Rule Mining</a>. Please feel free to comment on the topic. You can also subscribe to this blog by clicking on the subscribe button on the right side of the page.</p>
<a name="pd_a_2751817"></a><div class="CSS_Poll PDS_Poll" id="PDI_container2751817" data-settings="{&quot;url&quot;:&quot;https://secure.polldaddy.com/p/2751817.js&quot;}" style=""></div><div id="PD_superContainer"></div><noscript><a href="https://polldaddy.com/p/2751817" target="_blank" rel="noopener noreferrer">Take Our Poll</a></noscript>