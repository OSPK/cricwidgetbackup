# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provider :digital_ocean do |provider, override|
    override.ssh.private_key_path = '~/.ssh/id_rsa'
    override.vm.box = 'digital_ocean'
    override.vm.box_url = "https://github.com/smdahlen/vagrant-digitalocean/raw/master/box/digital_ocean.box"

    provider.token = '26501a37aeaaef1f50d41a34b3272f8158495d43b5a01058e85584cdf4dcf36e'
    provider.image = 'ubuntu-14-04-x64'
    provider.region = 'nyc2'
    provider.size = '512mb'
  end
  config.vm.provider :local do |provider, override|
    override.vm.box = 'ubuntu/trusty64'
    override.vm.network "forwarded_port", guest: 80, host: 8080
    override.vm.network "forwarded_port", guest: 5000, host: 8050
    override.ssh.forward_agent = true
  end
  config.vm.hostname = "score.dailypakistan.com.pk"

  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "forwarded_port", guest: 5000, host: 8050
  # config.vm.network "private_network", ip: "192.168.33.10"
  # config.vm.network "public_network"
  # config.ssh.forward_agent = true
  # config.vm.synced_folder "./code", "/home/vagrant/code", type: "rsync", rsync__exclude: "./code/env/"
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: [".git/", ".vagrant/", ".env/"]

  config.vm.provision "file", source: "tmp/default", destination: "/tmp/default"
  config.vm.provision "file", source: "tmp/crico.conf", destination: "/tmp/crico.conf"
  config.vm.provision "shell", path: "./provisioner"
  config.vm.provision "shell", path: "./always_run", run: "always"
end
