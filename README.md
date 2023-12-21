## igoLib-auto
### v2.0
using websockets & advanced queue logic
### v2.1
Optimized queuing logic~: 0.3s ahead of open time, we begin to send queue messages to the server
### v3.0
compatible for mutil users, clearer code logic   
instead of one send one recv (instead of recv immediately after send)  
before the server starts 0.8s or so, we begin to continuously send queue msg without recv!  
when the server start we recv all the msg we sent and if still in queue, switch into that one send one recv mode  
~~this version is aimed to prereserve seat for a HUELer, thx a lot.~~
### v4.0
**OOP!**  
class User and some raw utils-functions in files like keep_reserve.py or keep_session.py are now static methods in class User, which is more easy and friendly to use.
### v4.1
- Some unnecessary files were removed, cookie_grab.py e.g, and these removed files are integrated into other files(utils_params.py)
- When it comes to multithreading, pay attention to shared resources! Deep copy of shared resources! (2023.11.2 Reasons for failure)
- The use of two libraries for websocket
- Scripts(.sh) for starting, closing, and restarting projects in the Linux shell
**unsolved bug/problem**  
`SSLError: SSL validation failed ... EOF occurred in violation of protocol #3359`  
I have met this problem from time to time, still never have it solved
### v4.2
compared with v4.1, try to fix the bug in v4.1 preserve_seat_tomorrow.ws4py_py. hope that it would work, god bless my code

**afterwards:**  
it really works! well, remember, time.sleep(0.01), sleep 0.01s or longer in my_socket.py self.opened() method, otherwise u'll be shocked by the number of msg u send to the server, really.
### v4.3
just save my code, ready for another new version

### v5.0
this version just seek for stability  
well, the result is not that good. I am still being troubled by the SSL problem mentioned in version v4.1 :(
### v5.1
- skip users in blacklist
- if not get the seat users want, just begin to scan the lib_layout list and choose the seat nobody choose

### todo
- to complete functions in my_email.py