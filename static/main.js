
var app=new Vue({
  el: '#app',
  data: {
    user: "",
    rides: ""
  },

  created: function () {
    $("#rideContainer").hide();
    $("#top-bar").hide();
    $("#signForm").hide();
  },

  methods:{
      createRide: function(destination, start, time) {
        let currentUser = app.user;
        let axiosConfig = {
            headers: {
                'Content-Type': 'application/json;charset=UTF-8',
                "Access-Control-Allow-Origin": "*",
            }
          };
        let postData = {StartLocation: start, DepartureTime: time, Destination: destination, Seats: 3, Flag: 0};
        axios.post('https://info3103.cs.unb.ca:65430/rides/' + currentUser, postData, axiosConfig)
        .then(function(response) {
          let id = /[^/]*$/.exec(response.data.uri)[0];
          app.rides.push({"rideId": id, "userName": currentUser, "startLocation": start, "destination": destination, "departureTime": time, "seats": 3});
          })
          .catch((err) => {
          });
      },

      deleteRide: function(ride) {
        axios.delete('https://info3103.cs.unb.ca:65430/rides/' + app.user + '/' + ride.rideId)
        .then(function (response){
          var index = app.rides.findIndex(i => i.rideId == ride.rideId);
          app.rides.splice(index, 1);
        })
        .catch(function(error){

        });
      },

      addRider: function(ride, event) {
        let found = ride.riders.find((element) => {return element == currentUser});
          if (found === undefined) { // rider is not already in ride
            ride.riders.push(currentUser);
            if(event.target.tagName == "BUTTON") {
              event.target.childNodes[0].classList.remove("fa-plus");
              event.target.childNodes[0].classList.add("fa-minus");
              event.target.classList.remove("btn-success");
              event.target.classList.add("btn-danger");

            } else if (event.target.tagName == "I") {
              event.target.classList.remove("fa-plus");
              event.target.classList.add("fa-minus");
              event.target.parentElement.classList.remove("btn-success");
              event.target.parentElement.classList.add("btn-danger");
            }

          } else {
            ride.riders.splice(ride.riders.indexOf(currentUser), 1);
            if(event.target.tagName == "BUTTON") {
              event.target.childNodes[0].classList.add("fa-plus");
              event.target.childNodes[0].classList.remove("fa-minus");
              event.target.classList.add("btn-success");
              event.target.classList.remove("btn-danger");

            } else if (event.target.tagName == "I") {
              event.target.classList.add("fa-plus");
              event.target.classList.remove("fa-minus");
              event.target.parentElement.classList.add("btn-success");
              event.target.parentElement.classList.remove("btn-danger");
            }
          }

      },

      login : function (){

      let axiosConfig = {
          headers: {
              'Content-Type': 'application/json;charset=UTF-8',
              "Access-Control-Allow-Origin": "*",
          }
      };

      let postData = {username: $("#username").val(), password: $("#password").val()}
      var app=this;

      axios.post('https://info3103.cs.unb.ca:65430/signin', postData, axiosConfig)
      .then(function(response) {
        app.user = response.data.user;
        $("#loginField").hide();
        $("#jumbo").hide();
        $("#rideContainer").show();
        $("#top-bar").show();
        })
        .catch((err) => {
        });

        axios.get('https://info3103.cs.unb.ca:65430/rides')
        .then(function (response){
          app.rides=response.data.rides;
        })
        .catch(function(error){
          app.rides='An error ocurred: '+error;

        });
      },//end login

      logout : function (){

            axios.delete('https://info3103.cs.unb.ca:65430/signin')
            .then(function (response){
              window.location.reload();
            })
            .catch((err) => {
              alert(err);
            });
        },

      signUpForm : function (){
        $("#LoginField").hide();
        $("#signForm").show();
        $("#dontHave").hide();
      },

      cancel : function (){
        window.location.reload();
      },
    }
  })//end Vue
