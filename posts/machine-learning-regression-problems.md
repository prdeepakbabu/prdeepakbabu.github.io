---
title: "Machine learning & Regression Problems"
date: "2016-06-11"
canonical: "https://prdeepakbabu.wordpress.com/2016/06/12/machine-learning-regression-problems/"
source: "wordpress"
---
<h1>Machine Learning &#8211; Linear Regression using gradient descent vs. neural network</h1>
<p>Machine learning or Supervised Learning broadly encompasses two classes of problems &#8211; regression and classification. Regression deals with predicting a continous variable while a classification problem deals with categorical prediction. As an example, predicting house price is a regression problem which can take any real number. While, email spam detection is a classification problem as the outcome is a special kind of categorical variable ie. binary (spam 1/ non-spam 0). Numerous algorithms have been built over the last few decades which falls under one of these two classes. The focus of this post will be regression techniques and will reserve another post for classification techniques. Feel free to <a href="https://prdeepakbabu.wordpress.com/?blogsub=confirming#subscribe-blog">subscribe</a>/bookmark this page for upcoming posts.</p>
<ul>
<li>Introduction &#8211; Regression</li>
<li>Algorithms
<ul>
<li>Oridinary Least Squares (OLS)</li>
<li>Gradient Descent</li>
<li>Neural Networks</li>
</ul>
</li>
<li>Comparison of Algorithms</li>
<li>Conclusions &amp; Inferences</li>
</ul>
<p>Regression Techniques helps to understand relationship of continous variable as a function of one of more independent aka explanatory variables. It can be considered as a curve fitting problem where we are interested in learning a function y = f(X) where X belongs to x1,x2,x3..xi which best fits the y. Now, how do we quantify best fit ? Most techniques uses some measure of error &#8211; SSE (sum-of-squared error) also called cost function aka objective function to quantify the quality of fit. We desire to learn parameters which gives the least error. So, formally we can define this as an optimization problem to minimize SSE given the parameters of function f(x).</p>
<p style="padding-left:30px;">Linear vs. Non-Linear : When y = f(x) takes the shape of y = a0 + a1 * x1 + a2 * x2 + .. + an * xn, we call this a linear regression where we are trying to fit a straight line to the curve. In non-linear we learn y = f(x) of more complex forms involving log, exponents, higher order polynomials of independent variables. For example y = a0 + a1 * log(x1) + a2 * e^x + a3* x^3.</p>
<p style="padding-left:30px;">Single vs. Multiple Regression : When y = f(x) has a more than one explanatory variable then called multiple regression.</p>
<p>Lets take a simple linear regression problem(dataset) and try to apply couple of algorithms and compare accuracy, complexity, run times.  We will conclude this post with in-depth understanding of techniques. Following three techniques have been explored in detail using R libraries. Feel free to download <a href="https://github.com/prdeepakbabu/Fundas/blob/master/Regression/Regression%20-%20ML%20Techniques.ipynb">notebook</a> and try running yourself, playing with parameters and plots available on my <a href="https://github.com/prdeepakbabu/Fundas/tree/master/Regression">github</a>. The notebooks are also available in <a href="https://rawgit.com/prdeepakbabu/Fundas/master/Regression/Regression%20-%20ML%20Techniques.html" target="_blank">html </a>so you can explore the charts &amp; documentation here. A high level summary is presented below, highly recommend checking the notebook here.</p>
<p>Link to jupyter notebook (code, charts &amp; data) <a href="https://github.com/prdeepakbabu/Fundas/tree/master/Regression">here</a></p>
<ol>
<li>Ordinary Least Squares<br />
A closed form solution uses matrix multiplication &amp; inverse to find parameters which minimize error (SSE). This is an anlaytic solution always finds a minima (of error). Looking the (x,y) plot we attempt fitting non-linear model using linear regression exploiting variable transformation techniques.</li>
<li>Gradient Descent<br />
A open form solution, which uses mathematical optimization by initializing parameters randomly and iteratively adjusting the parameters depending on the gradient that reduces SSE. We start with learning rate of 0.01 and iterate for 120000 times.</li>
<li>Neural Networks<br />
Now, generally popular among AI (Artificial Intelligence) practitioners which mimics working of human brain, modelling hidden layers with weights propagating across layers between input &amp; output nodes. Internally, uses gradient descent with back-propagation to learn the weights. We use a 3 hidden layers, each with 3 nodes and train a neural network model. Input &amp; Output are single nodes as we have a single predictor and a single explanatory variable.</li>
</ol>
<p><img loading="lazy" data-attachment-id="8560" data-permalink="https://prdeepakbabu.wordpress.com/2016/06/12/machine-learning-regression-problems/nnet_vis_1/" data-orig-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg" data-orig-size="2100,2100" data-comments-opened="1" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;0&quot;}" data-image-title="nnet_vis_1" data-image-description="" data-image-caption="" data-medium-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg?w=300" data-large-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg?w=545" class="  wp-image-8560 alignleft" src="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg" alt="nnet_vis_1" width="262" height="262" srcset="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg?w=262&amp;h=262 262w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg?w=524&amp;h=524 524w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg?w=150&amp;h=150 150w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/nnet_vis_1.jpg?w=300&amp;h=300 300w" sizes="(max-width: 262px) 100vw, 262px" /></p>
<p><img loading="lazy" data-attachment-id="8557" data-permalink="https://prdeepakbabu.wordpress.com/2016/06/12/machine-learning-regression-problems/models_1/" data-orig-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg" data-orig-size="2100,2100" data-comments-opened="1" data-image-meta="{&quot;aperture&quot;:&quot;0&quot;,&quot;credit&quot;:&quot;&quot;,&quot;camera&quot;:&quot;&quot;,&quot;caption&quot;:&quot;&quot;,&quot;created_timestamp&quot;:&quot;0&quot;,&quot;copyright&quot;:&quot;&quot;,&quot;focal_length&quot;:&quot;0&quot;,&quot;iso&quot;:&quot;0&quot;,&quot;shutter_speed&quot;:&quot;0&quot;,&quot;title&quot;:&quot;&quot;,&quot;orientation&quot;:&quot;0&quot;}" data-image-title="models_1" data-image-description="" data-image-caption="" data-medium-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg?w=300" data-large-file="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg?w=545" class="alignnone  wp-image-8557" src="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg" alt="models_1" width="244" height="244" srcset="https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg?w=244&amp;h=244 244w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg?w=488&amp;h=488 488w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg?w=150&amp;h=150 150w, https://prdeepakbabu.wordpress.com/wp-content/uploads/2016/06/models_1.jpg?w=300&amp;h=300 300w" sizes="(max-width: 244px) 100vw, 244px" /></p>
<p>Lets compare which of the models performs well in terms of best fitting the data. Please note, here I am not using train/test approach as idea here is emphasis on technique. So we are talking about training error here. Lets use RMSE (root mean square error) to compare the three models</p>
<table>
<tbody>
<tr>
<td><strong>RMSE</strong><br />
<strong>Ordinary Least Squares</strong></td>
<td><strong>RMSE</strong><br />
<strong>Gradient Descent</strong></td>
<td><strong>RMSE</strong><br />
<strong>Neural Network</strong></td>
</tr>
<tr>
<td>0.000534</td>
<td>0.000984</td>
<td>0.000278</td>
</tr>
</tbody>
</table>
<p>Looking at RMSE, neural network seems to be doing a great job in learning the data. NN is known to have good memorizing capability and causes over fitting leading high variance system. Also we must note, Neural Network did not involve any kind of feature engineering we just passed x values unlike in other methods, we had x^2 as feature. So NN is known to be great at identifying latent features without explicit need for feature engineering usually done by domain experts of respective problem spaces.</p>
<p>Table below explains more about each of the 3 techniques, how they differ, when to use-what etc.</p>
<table>
<tbody>
<tr>
<td><strong>Ordinary Least Squares</strong></td>
<td><strong>Gradient Descent</strong></td>
<td><strong>Neural Network</strong></td>
</tr>
<tr>
<td>Closed Form<br />
Analytic Solution</td>
<td>Open Form<br />
Iterative Optimization</td>
<td>&#8211;</td>
</tr>
<tr>
<td>Slow, involves matrix inverse computation</td>
<td>Fast for large datasets</td>
<td>Slow, training usually done on GPUs which can handle matrix computations easily</td>
</tr>
<tr>
<td>&#8211;</td>
<td>Hyperparameters &#8211; epoch(iterations), alpha-learning rate</td>
<td>Hyperparameters &#8211; hidden layers, nodes, activation fn., learning rate</td>
</tr>
<tr>
<td>Feature Engineering Required</td>
<td>Feature Engineering Required</td>
<td>Little/No Feature Engineering Needed</td>
</tr>
<tr>
<td>More data is good</td>
<td>More data is good</td>
<td>While more data is good, NN requires a lot of data for good generalization</td>
</tr>
<tr>
<td>Good Interpretability. Easy to communicate findings</td>
<td>Good Interpretability. Easy to communicate findings</td>
<td>Blackbox, difficult to explain suffers from interpretability</td>
</tr>
<tr>
<td>Most commonly used for building offline models on small datasets</td>
<td>Commonly used for large scale learning involving thousands of features</td>
<td>Used commonly in text/vision/speech &#8211; mostly uses two variants CNN and RNN architectures.</td>
</tr>
<tr>
<td>Tools: R,SAS,Python</td>
<td>Tools: Python,R</td>
<td>Tools: Deeplearning4j, Theano, Python, R, Tensorflow</td>
</tr>
<tr>
<td>&#8211;</td>
<td>Can get stuck in local minima, due to bad initialization/learning rate</td>
<td>Can get stuck in local minima, due to bad initialization/learning rate</td>
</tr>
</tbody>
</table>
<p>What we did not talk about, but important in this context ?</p>
<ul>
<li>Cross Validation</li>
<li>Feature engineering and reduction(PCA)</li>
<li>Hyperparameter tuning</li>
<li>Sampling</li>
<li>Objective Functions</li>
<li>Regularization L1/L2</li>
<li>Interaction Effects</li>
</ul>
<p>A lot of content to digest here, feel free to share any feedback/comment you have about any part of the blog post &#8211; would love to chat around. I will be back with a similar post on classification in coming days comparing logistic regression, decision trees, random forest(ensembles) and neural networks.</p>