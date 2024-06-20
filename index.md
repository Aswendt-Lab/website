---
title: Home
layout: home
---

# Neuroimaging and Neuroengineering of Experimental Stroke

# *This website is currently under construction. Updates will follow soon.*

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
