---
title: Reading list
permalink: /reading-list.html
---

The papers the lab is reading and discussing together.

{% assign reading_list = site.data.reading_list %}
{% if reading_list.items.size > 0 %}
<div class="reading-list-table">
<table>
  <thead><tr><th scope="col">Manuscript</th><th scope="col">Posted</th><th scope="col">Links</th></tr></thead>
  <tbody>
  {% for item in reading_list.items %}
  <tr>
    <td>{{ item.title | escape }}</td>
    <td><time datetime="{{ item.posted_at | escape }}">{{ item.posted_at | date: "%d %b %Y" }}</time></td>
    <td>{% for link in item.links %}{% if forloop.first == false %} · {% endif %}<a href="{{ link.url | escape }}" target="_blank" rel="noopener noreferrer">{{ link.label | escape }}</a>{% endfor %}</td>
  </tr>
  {% endfor %}
  </tbody>
</table>
</div>
{% else %}
<p>The reading list is empty for now.</p>
{% endif %}
