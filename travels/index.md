---
layout: default
title: Travels
---

## Travelogues

<ul>
{% for page in site.pages %}
  {% if page.section == "travelogue" %}
    <li>
      <a href="{{ page.url | relative_url }}">{{ page.title }}</a>
    </li>
  {% endif %}
{% endfor %}
</ul>
