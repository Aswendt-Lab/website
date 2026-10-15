# Aswendt Lab website

Jekyll website for the Aswendt Lab’s research on experimental stroke, neuroimaging, and neuromodulation.

**Live website:** https://aswendt-lab.github.io/website/

## Local development

Use a modern Ruby installation compatible with Bundler 2.5.10 (Ruby 3.1 or newer).

```sh
gem install bundler -v 2.5.10
bundle install
bundle exec jekyll serve
```

Open http://localhost:4000/website/. To check a production build:

```sh
JEKYLL_ENV=production bundle exec jekyll build
```

The generated site is written to `_site/`, which is ignored by Git. Dependencies are pinned in `Gemfile.lock`; keep this file when updating the site.

## Editing content

- `index.md`: homepage, research introduction, featured publication, and news highlights.
- `_data/partners.yml`: collaborator names, institutions, and logos shown on the homepage.
- `projects.md`: research themes; `software.md`: AIDA tools, data workflows, tutorials, and poster downloads.
- `opportunities.md`: student inquiries and application guidance.
- `paper.md`, `team.md`, `news.md`: publications, team profiles, and news archive.
- `contact.md`, `imprint.md`: contact details and legal notice.
- `assets/main.scss`: shared black theme, responsive layouts, and accessible focus styles.
- `_includes/footer.html`: footer navigation; `_layouts/landing.html`: homepage layout.

Use descriptive image alternative text. Add `loading="lazy"` to images below the first screen. Homepage highlights are curated manually; update them when adding news or publications.

## Deployment

The site uses GitHub Pages-compatible Jekyll dependencies. `_config.yml` sets `url: https://aswendt-lab.github.io` and `baseurl: /website`. Use Jekyll’s `relative_url` filter for internal links so the project path is preserved.

Deployment is managed through the repository’s GitHub Pages settings. Confirm the configured branch or workflow there before publishing; local edits alone do not deploy the site.

## Contributing

[Open an issue](https://github.com/Aswendt-Lab/website/issues) or submit a pull request. Include a description and screenshots for visual changes. Before submitting, build the site and check navigation, mobile layouts, and links.

Explore the lab’s [software repositories](https://github.com/Aswendt-Lab).
