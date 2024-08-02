---
title: News
layout: page
---

{% for post in site.posts limit:2 %}
   <div class="post-preview">
       <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
       <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
       {{ post.content | split:'<!--break-->' | first }}
       {% if post.content contains '<!--break-->' %}
           <a href="{{ post.url }}">
               read more
           </a>
       {% endif %}
       <hr>
   </div>
{% endfor %}


### 10/2023 First prize for Aref Kalantari at MRI Together Session
European Society for Magnetic Resonance in Medicine and Biology 2023 in Basel, Switzerland
<div style="white-space: nowrap;">
  <img src="img/AK_ESMRMB_2023_3.jpg" alt="Cover" style="width: auto; height: 200px; display: inline-block;"/>
  <img src="img/AK_ESMRMB_2023_1.jpg" alt="Cover" style="width: auto; height: 200px; display: inline-block;"/>
  <img src="img/AK_ESMRMB_2023_2.jpg" alt="Cover" style="width: auto; height: 200px; display: inline-block;"/>
</div>


### 07/2023 Invited talk at Charité Berlin
For the seminar series of the Department of Experimental Neurology, Markus gave a presentation on "Demystifying astrogliosis after cortical stroke in mice using functional connectivity analysis". Markus together with Aref and Fatemeh enjoyed a fruitful discussion with our long-standing collaboration partner Prof. Philipp Boehm-Sturm and colleagues. 
<div style="white-space: nowrap;">
  <img src="img/MA_Berlin_Charite_2023_2.jpeg" alt="Cover" style="width: auto; height: 200px; display: inline-block;"/>
  <img src="img/MA_Berlin_Charite_2023_3.jpeg" alt="Cover" style="width: auto; height: 200px; display: inline-block;"/>
  <img src="img/MA_Berlin_Charite_2023_1.jpg" alt="Cover" style="width: auto; height: 200px; display: inline-block;"/>
</div>


