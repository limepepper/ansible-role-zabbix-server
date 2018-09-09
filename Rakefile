
desc 'Rubocop of new code'
task :rubocop do
  puts 'Execution of Rubocop linting tests'
  sh 'rubocop .'
end

desc 'Ansible lint role directory'
task :ansible_lint do
  puts 'Execution of Ansible Lint'
  sh 'ansible-lint .'
end

desc 'yamllint role directory'
task :yamllint do
  puts 'Execution of yamllint'
  sh 'yamllint .'
end

desc 'flake8 role directory'
task :flake8 do
  puts 'Execution of flake8'
  sh 'flake8 .'
end

desc 'Run linting commands'
task lint: %w[rubocop yamllint ansible_lint flake8] do
  # Your code goes here
end

desc 'Run setup'
task :setup do
  # Your code goes here
  puts 'bundle exec stuff'
  sh 'bundle install'
  sh 'bundle update'
end

# desc 'Foodcritic of new code'
# task :foodcritic do
#   puts 'Running Foodcritic linting tests...'
#   sh 'foodcritic . -f any'
# end

desc 'Build VM with cookbook'
task :create do
  puts 'run kitchen task create'
  sh 'KITCHEN_LOCAL_YAML=.kitchen.digitalocean.yml bundle exec '\
          "kitchen create #{ENV['suite']}-#{ENV['platform']}"
end

desc 'Converge VM with cookbook'
task :converge do
  puts 'run kitchen tasks'
  sh 'KITCHEN_LOCAL_YAML=.kitchen.digitalocean.yml bundle exec '\
          "kitchen converge #{ENV['suite']}-#{ENV['platform']}"
end

desc 'Build VM with cookbook'
task :verify do
  puts 'run kitchen tasks'
  sh 'KITCHEN_LOCAL_YAML=.kitchen.digitalocean.yml bundle exec '\
          "kitchen verify #{ENV['suite']}-#{ENV['platform']}"
end

desc 'Destroy VM'
task :destroy do
  puts 'run kitchen tasks'
  sh 'KITCHEN_LOCAL_YAML=.kitchen.digitalocean.yml bundle exec '\
          "kitchen destroy #{ENV['suite']}-#{ENV['platform']}"
end
