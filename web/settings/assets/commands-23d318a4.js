import{_ as c,q as p,l as d,m as r,A as m,K as l,v as u}from"./vendor-5f866419.js";import"./vendor-sortablejs-793d687d.js";const g={name:"ChargePointCommandsOpenwbPro",props:{configuration:{type:Object,required:!0},chargePointId:{default:void 0}},methods:{async triggerUpdate(){let s=new FormData;s.append("command","update"),s.append("data",'{"ip_address":"'+this.configuration.ip_address+'"}');const a="Die Aktualisierung der openWB Pro wird gestartet...",n=Math.floor(Date.now()/1e3);this.$store.commit("addTopic",{topic:"openWB/command/"+this.$root.mqttClientId+"/messages/"+n,payload:{source:"command",type:"info",message:a,timestamp:n}}),console.log(location),this.axios.post(location.protocol+"//"+location.host+"/openWB/web/settings/modules/charge_points/openwb_pro/commands.php",s,{timeout:5e3}).then(e=>{console.log("POST response",e.data);const t="Die Aktualisierung der openWB Pro wurde erfolgreich gestartet.",o=Math.floor(Date.now()/1e3);this.$store.commit("addTopic",{topic:"openWB/command/"+this.$root.mqttClientId+"/messages/"+o,payload:{source:"command",type:"success",message:t,timestamp:o}})}).catch(e=>{var t="Aktualisierung fehlgeschlagen!<br />";e.response?(console.log(e.response.status,e.response.data),t+=e.response.status+": "+e.response.data):e.request?(console.log(e.request),t+="Es wurde keine Antwort vom Server empfangen."):(console.log("Error",e.message),t+="Es ist ein unbekannter Fehler aufgetreten.");const o=Math.floor(Date.now()/1e3);this.$store.commit("addTopic",{topic:"openWB/command/"+this.$root.mqttClientId+"/messages/"+o,payload:{source:"command",type:"danger",message:t,timestamp:o}})})}}},h={class:"charge-point-commands-openwbpro"};function f(s,a,n,e,t,o){const i=p("openwb-base-button-input");return d(),r("div",h,[m(i,{title:"Ladepunkt aktualisieren",buttonText:"Update anfordern",subtype:"success",disabled:n.configuration.ip_address==null,onButtonClicked:o.triggerUpdate},{help:l(()=>[u(" Mit diesem Befehl können Sie die Aktualisierung der openWB Pro anstoßen. Bitte beachten Sie, dass kein Fahrzeug angesteckt ist. ")]),_:1},8,["disabled","onButtonClicked"])])}const w=c(g,[["render",f],["__file","/opt/openWB-dev/openwb-ui-settings/src/components/charge_points/openwb_pro/commands.vue"]]);export{w as default};