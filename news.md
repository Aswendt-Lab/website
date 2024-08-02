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
{% endfor %}

### First prize for Aref Kalantari 
European Society for Magnetic Resonance in Medicine and Biology 2023 in Basel, Switzerland
<div style="text-align: left;">
  <img src="img/AK_ESMRMB_2023_1.jpg" alt="Cover" style="width: 300px; height: auto;"/>
</div>
<div style="text-align: right;">
  <img src="img/AK_ESMRMB_2023_2.jpg" alt="Cover" style="width: 600px; height: auto;"/>
</div>
