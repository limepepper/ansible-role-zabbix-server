skiplist = attribute('skiplist',
                     description: 'list of controls to skip',
                     default: [],
                     required: true)

# my_services = yaml(content: inspec.profile.file('services.yml')).params
vars_json = json('/var/cache/ansible/attributes/hostvars.json')

vars = vars_json.params

control 'check-attributes' do
  impact 0.6
  title "Check attribtues for node: #{vars['ansible_hostname']}"
  desc '      Checking the hostvars cache is sensible  '
  describe file('/var/cache/ansible/attributes/hostvars.json') do
    it { should exist }
    #  its('mode') { should cmp 0644 }
  end
end

#                           _            _            _
#     __ _ _ __   __ _  ___| |__   ___  | |_ ___  ___| |_ ___
#    / _` | '_ \ / _` |/ __| '_ \ / _ \ | __/ _ \/ __| __/ __|
#   | (_| | |_) | (_| | (__| | | |  __/ | ||  __/\__ \ |_\__ \
#    \__,_| .__/ \__,_|\___|_| |_|\___|  \__\___||___/\__|___/
#         |_|

control 'check-apache' do
  impact 0.6
  title "Check apache for node: #{vars['ansible_hostname']}"
  desc ' test that zabbix is listening '

  describe service(vars['apache_service']) do
    it { should be_enabled }
    it { should be_installed }
    it { should be_running }
  end

  url = 'http://localhost/zabbix/'

  describe http(url, ssl_verify: false) do
    its('status') { should be_in [200] }
    its('body') { should match(/Zabbix SIA/) }
    # its('headers.name') { should eq 'header' }
    its('headers.Content-Type') { should match(%r{text\/html}) }
  end

  # describe package('php') do
  #   it { should be_installed }
  # end

  describe command('php --version') do
    its('stdout') { should match(/PHP/) }
  end

  describe port(80) do
    it { should be_listening }
  end

  describe file('/tmp') do
    it { should be_directory }
  end

  describe http('http://localhost/zabbix/api_jsonrpc.php',
                # params: { format: 'html' },
                method: 'POST',
                headers: { 'Content-Type' => 'application/json-rpc' },
                data: '{"jsonrpc":"2.0","method":"apiinfo.version","id":1,"auth":null,"params":{}}') do
    its('status') { should cmp 200 }
    its('body') { should match(/"result":"3.4/) }
    its('headers.Content-Type') { should match(/^application\/json/) }
  end

  describe http('http://localhost/zabbix/api_jsonrpc.php',
                # params: { format: 'html' },
                method: 'POST',
                headers: { 'Content-Type' => 'application/json-rpc' },
                data: '{"jsonrpc":"2.0","method":"user.login","id":1,"params":{"password":"'+vars['zabbix_web_admin_pass']+'","user":"Admin"}}') do
    its('status') { should cmp 200 }
    its('body') { should match(/"result":/) }
    its('headers.Content-Type') { should match(/^application\/json/) }
  end

  # describe file('hello.txt') do
  #   its('content') { should match 'Hello World' }
  # end
end
