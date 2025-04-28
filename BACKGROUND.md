# Setup a VPN for your org or email verification for marzban

If you live in a part of the world where you never have to bother with VPNs, this post if not for you. Yet, if even your grandma already heard that she needs to access Youtube or any other web resource - welcome aboard!

Sadly, internet became fragmented over the last few years. You move from one country to another and to your surprise find that REPLACE_WITH_YOUR_FAVORITE_RESOURCE is all of a sudden is not available anymore. WTF? 

It is a minor inconvenience when it is a feed with cat memes, but a major problem when it is, say, Youtube.

About a year ago I left London to go back to school. As you can guess, the school network (network provider actually, but who cares?) had an extensive blacklist. It hurt my studies and studies of other students. I decided to setup a VPN for me and other students. Well, I am a damn computer science student, aren't I?

Below if the blueprint on how to setup an VPN for your entire org (my uni in this case) in broad strokes.

You will need:

- Any VPS with a good network connection;
- [marzban](https://github.com/Gozargah/Marzban) - SOTA proxy management tool powered by [Xray-core](https://github.com/XTLS/Xray-core);
- [marzban-verify](https://github.com/aigoncharov/marzban-verify) - sidecar for mazrban to create new accounts with email verification;
- Telegram account.

What you will get:
- A Telegram bot where people can create VPN accounts on their own as long as they have access to their org emails. For instance, you can provide VPN access to all email holder at `@wtf.com`.
- Sane defaults with a 3 month expiration date and 50 GB traffic limit for new accounts (can be changed).

The blueprint:
- Find a decent VPS. Do not trust speed filters on aggregators. They lie. I had to manually search Reddit for a shortlist of suitable providers and then test them one by one. Do not go with the largest ones if you want your VPN to last. The largest providers are the first targets for censors.
- Install [marzban](https://github.com/Gozargah/Marzban?tab=readme-ov-file#installation-guide). Set `DOCS` to `True`.
- Get [SSL](https://gozargah.github.io/marzban/en/examples/marzban-ssl) and optionally set it up to [work on one port](https://gozargah.github.io/marzban/en/examples/all-on-one-port). I have a simpler Haproxy config that still works well:
  ```
    listen front     
	    mode tcp     
	    bind *:443      
	    tcp-request inspect-delay 5s     
	    tcp-request content accept if { req_ssl_hello_type 1 }     
	    
	    use_backend marz if { req.ssl_sni -i end  ADDRESS_OF_MY_VPN_SERVER }
	    use_backend reality 
	    
	backend reality     
		mode tcp     
		server srv1 127.0.0.1:12000 send-proxy-v2 tfo  
		
	backend marz     
		mode tcp     
		server srv1 127.0.0.1:10000
	```
- Use [BotFather](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) in Telegram to create a new bot that your colleagues are going to use to setup their accounts.
- Setup [marzban-verify](https://github.com/aigoncharov/marzban-verify?tab=readme-ov-file#quickstart). Currently, it can send confirmation emails by setting up a standalone SMTP server (prone to being identified as spam, also some VPS hosters block port 25) or by using your own Exchange email (popular in enterprise envs).
- Profit!

No wise closing words. Just send your PRs if you need more email providers.
