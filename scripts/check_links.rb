# Check rendered internal links and fragment targets without contacting external sites.
require 'nokogiri'
require 'uri'
require 'pathname'
require 'yaml'
root = Pathname.new(ARGV[0] || '_site').expand_path
baseurl = YAML.load_file('_config.yml').fetch('baseurl', '')
documents = {}
Dir[root.join('**/*.html')].each { |p| documents[p] = Nokogiri::HTML(File.read(p)) }
errors = []
documents.each do |source, document|
  document.css('a[href], img[src], script[src], link[href], source[src]').each do |node|
    target = node['href'] || node['src']
    next if target.nil? || target.empty? || target.match?(%r{\A(?:[a-z][a-z0-9+.-]*:|//)}i)
    path, fragment = target.split('#', 2)
    path = URI::DEFAULT_PARSER.unescape(path.split('?', 2).first.to_s)
    absolute = if path.empty?
      Pathname.new(source)
    elsif path.start_with?('/')
      if !baseurl.empty? && !(path == baseurl || path.start_with?(baseurl + '/'))
        errors << "#{source}: path bypasses baseurl: #{target}"
        next
      end
      root.join(path.delete_prefix(baseurl).delete_prefix('/'))
    else
      Pathname.new(source).dirname.join(path)
    end.cleanpath
    absolute = absolute.join('index.html') if absolute.directory?
    unless absolute.file?
      errors << "#{source}: missing file: #{target}"
      next
    end
    if fragment && !fragment.empty? && documents[absolute.to_s]
      id = URI::DEFAULT_PARSER.unescape(fragment)
      ids = documents[absolute.to_s].css('[id], a[name]').map { |n| n['id'] || n['name'] }
      errors << "#{source}: missing anchor: #{target}" unless ids.include?(id)
    end
  end
end
abort errors.join("\n") unless errors.empty?
puts "PASS: internal links, assets, and fragment targets across #{documents.length} rendered pages."
