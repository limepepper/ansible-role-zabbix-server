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
  desc "      Checking the hostvars cache is sensible  "
  describe file('/var/cache/ansible/attributes/hostvars.json') do
    it { should exist }
    #  its('mode') { should cmp 0644 }
  end
end

control 'check-zabbix-users-1' do
  impact 0.6
  title "Check attribtues for node: #{vars['ansible_hostname']}"
  desc "      Checking the hostvars cache is sensible  "

  describe (vars['zabbix_db_user']).to_s.empty? do
    it { should_not eq true }
  end

  describe (vars['zabbix_db_pass']).to_s.empty? do
    it { should_not eq true }
  end

  describe (vars['zabbix_db_host']).to_s.empty? do
    it { should_not eq true }
  end

  describe (vars['zabbix_db_name']).to_s.empty? do
    it { should_not eq true }
  end

  sql = mysql_session(vars['zabbix_db_user'], vars['zabbix_db_pass'])

  describe sql.query("select * from #{vars['zabbix_db_name']}.users WHERE alias = 'user_exists_and_disabled';") do
    its('stdout') { should match(/guest1gergrg/) }
  end
end