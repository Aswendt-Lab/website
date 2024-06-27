---
title: Home
layout: page
---
![Cover page illustration decoding stroke](assets/images/CoverDecodeStroke.png)

# Neuroimaging and Neuroengineering of Experimental Stroke
## Our Mission
One-third of stroke patients suffer from long-term disabilities, and functional recovery is often incomplete. By integrating advanced neurotechniques, such as in vivo MRI, viral tracing, and light sheet microscopy, we aim to uncover the cellular and neural circuit mechanisms underlying motor recovery after experimental stroke. Our research explores the development of motor deficits, such as spastic muscle tone, and creates innovative neuromodulation and regeneration paradigms to enhance endogenous plasticity mechanisms and improve stroke recovery. We are committed to open science, FAIR data workflows and standardization iniatives, ensuring our research data and software projects are publicly accessible.   

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
