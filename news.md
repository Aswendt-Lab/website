---
title: News
layout: page
---

{% for post in site.posts limit:2 %}
   <div class="post-preview">
       <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
       <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
       {% assign content_parts = post.content | split: '<!--break-->' %}
       {{ content_parts[0] }}
       {% if content_parts.size > 1 %}
           <a href="{{ post.url }}">
               read more
           </a>
       {% endif %}
       <hr>
   </div>
{% endfor %}
