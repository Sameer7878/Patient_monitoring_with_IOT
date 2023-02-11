/*
This JavaScript is created by Sameer Shaik, IT
This helps to connect Websockets which are accepted by backend

 */

//DOM variables Initialised
const Anime_Array=['Monkey D. Luffy','Edward Elric',' Naruto Uzumaki','Johan','Goku','Spike Spiegel','Vegeta','Sailor Moon','Shinji Ikari','Himura Kenshin','L','Tanjiro','Roronoa Zoro','Jotaro Kujo','Arsene Lupin','Guts','Kakashi','Levi Ackerman','Motoko Kusanagi','Gon Freecss','Dio Brando','Light Yagami','Lelouch Lamperouge','Vash the Stampede','Astro Boy']
const randIndex = Math.floor(Math.random() * Anime_Array.length);
var your_name=Anime_Array[randIndex];
var img_prefix='../static/imgs/';
let chatFrnd=document.getElementById("chat-friend");
let chatRand=document.getElementById("chat-random");
const msgerForm = document.getElementsByClassName("msger-inputarea")[0];
const msgerInput = document.getElementsByClassName("msger-input")[0];
const msgerChat = document.getElementsByClassName("msger-chat")[0];
var your_id=Math.floor(Math.random() * 100);
const protocol = window.location.protocol.includes('https') ? 'wss': 'ws';
const ws = new WebSocket(`${protocol}://${location.host}/EstablishConn/${your_id}`);
var modal = document.getElementById("myModal");
const chatfrnd_input=document.getElementById('chatfrnd-input');
const btn_option=document.getElementById('btn-options');
const msg_info=document.getElementById('msg-coninfo');

//-------------------------------------------------------------------------------

        //This is Sleep funtion like time.sleep in python
        let sleep = ms => {
            return new Promise(resolve => setTimeout(resolve, ms));
        };

        // on load of page modal pop
         window.onload = function() {
            modal.hidden =false;
        }
        //This updates live connections count on top right
         function updatelivecount(cou){
            document.getElementById("countnum").textContent=cou;
        }

        // this funtion for chat with frnd mode button
         chatFrnd.onclick=function (){
            chatfrnd_input.style.display='flex';
            btn_option.hidden=true;
        }

        //This funtion for 'connect' button
        function Est() {
            var frnd_id=document.getElementById("id2-input");
            var your_id=document.getElementById("id1-input");
            if(frnd_id.value>0){
                ws.send(JSON.stringify({"type":"FrndKey","your_id":your_id.value,"frnd_id":frnd_id.value}));
                //modal.style.display = "none";
                chatfrnd_input.style.display='none';
                msg_info.innerHTML='<p>Waiting For Connection...</p>';
            }
            else{
                frnd_id.style.borderColor="red";
            }
        }
        // this funtion for back button
        document.getElementById('back-btn').onclick=function (){
            chatfrnd_input.style.display='none';
            btn_option.hidden=false;

        }
        // this function for chat random button
        chatRand.onclick=function (){
            var your_id=document.getElementById("id1-input");
            ws.send(JSON.stringify({"type":"RandConn","your_id":your_id.value}))
            btn_option.hidden=true;
            msg_info.innerHTML='<p>Waiting For Connection...</p>';

        }

        // this funtions waits for msg send by websocket and update the msg by type
        ws.onmessage = function (event) {
            //var douquot=event.data.replace(/'/g, '"');
            var jsoda = JSON.parse(event.data);
            const mtype= jsoda.type;
            if (mtype==="uniqId"){
                document.querySelector("#id1-input").value = jsoda.Id;
            }
            else if(mtype==='conncount'){
                updatelivecount(jsoda.status)
            }
            else if (mtype==="Connection"){
                if(jsoda.status===true){
                    msg_info.innerHTML='<p>Connection Established</p>';
                    document.querySelector("#id2-input").value=jsoda.frnd_id;
                    sleep(1000).then(() => {
                        modal.hidden=true;
                    });
                }
                else if(jsoda.status==="Refuse"){
                    msg_info.innerHTML='<p>Connection Refused</p>';
                    sleep(1000).then(() => {
                        msg_info.hidden=true;
                        chatfrnd_input.style.display='flex';
                    });
                }
                else{
                    msg_info.innerHTML=`<p>${jsoda.status}</p>`;
                }
            }
            else {
                if(mtype==='CloseConn'){
                    msgerChat.insertAdjacentHTML("beforeend", `<div class="msg-leave">${jsoda.content}</div>`)
                    msgerChat.scrollTop += 500;
                    sleep(3000).then(() => {
                        msgerChat.innerHTML = '';
                        modal.hidden = false;
                        document.querySelector("#id2-input").value='';
                        btn_option.hidden=false;
                        msg_info.innerHTML='';

                    });
                }
                else{
                    appendMessage(jsoda.name, img_prefix+jsoda.img_no+'.jpeg', "left", jsoda.content);
                }
            }
        };

         //this funtion helps to send msg to websocket server with json data consists of destination and content of msg
        msgerForm.addEventListener("submit", event => {
            event.preventDefault();
            const fri_id = document.getElementById('id2-input');
            const your_id = document.getElementById('id1-input');
            const msgText = msgerInput.value;
            if (!msgText) return;
            const msgdata = {};
            msgdata.type="msg"
            msgdata.name=your_name;
            msgdata.msg = msgText;
            msgdata.img_no=randIndex+1;
            msgdata.friend_id = fri_id.value;
            ws.send(JSON.stringify(msgdata));
            appendMessage(your_name, img_prefix+(randIndex+1)+'.jpeg', "right", msgText);
            msgerInput.value = "";
            msgerInput.focus();
        });

        //this funtion helps to append msg on the msger-chat space
        function appendMessage(name, img, side, text) {
            //   Simple solution for small apps
            var today  = new Date();
            const msgHTML = `
                        <div class="msg ${side}-msg">
                          <div class="msg-img" style="background-image: url(${img})"></div>
                          <div class="msg-bubble">
                            <div class="msg-info">
                              <div class="msg-info-name">${name}</div>
                              <div class="msg-info-time">${today.toLocaleTimeString()}</div>
                            </div>

                            <div class="msg-text">${text}</div>
                          </div>
                        </div>
            `;

            msgerChat.insertAdjacentHTML("beforeend", msgHTML);
            msgerChat.scrollTop += 500;
        }
/*
End of the file
Thank you
*/