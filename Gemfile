#
# This file was originally generated by ansible. if you run ansible again
# your changes will be lost
#

source 'https://rubygems.org'

# jenkins is remote, so no local paths
if ENV['JENKINS_HOME']
  gem 'inspec', git: 'https://github.com/limepepper/inspec', branch: 'master'
  gem 'kitchen-digitalocean',
      git: 'https://github.com/limepepper/kitchen-digitalocean',
      branch: 'firewall-add'
  gem 'kitchen-inspec'

elsif ENV['LOCAL_DEV']
  gem 'inspec'
  gem 'kitchen-digitalocean', path: '/home/tomhodder/git/kitchen-digitalocean'
  gem 'kitchen-inspec'
  gem 'kitchen-vagrant'

else
  gem 'inspec'
  gem 'kitchen-digitalocean'
  gem 'kitchen-inspec'
  gem 'kitchen-vagrant'
end

group :testing do
  gem 'kitchen-ansiblepush'
  gem 'net-ssh'
  gem 'test-kitchen', '~> 1.8'
end
