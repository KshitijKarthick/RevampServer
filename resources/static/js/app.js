var app = angular.module('RegApp',['ngRoute']);

app.factory('EventsFactory',['$http',function($http){
    var factory = {};
    var events = [{name:'Some Event', pay: false},{name:'Some other event with a very big name', pay: false},{name:'bfc', pay: false},{name:'sdsf', pay: false}];
    factory.getEvents = function(usn){
        this.events = events;
        this.usn = usn;
        $http.get('/eventsOf/'+usn )
        .success(function(data,status,headers,config){
            console.log(data)
        })
        .error(function(data,status,headers,config){
            console.log("Error");
        })
        return events;
    }
    return factory;
}]);

app.controller('USNController', ['$scope', '$location', 'EventsFactory', function($scope, $location, EventsFactory){
    $scope.data ={}
    $scope.data.usn = '';
    $scope.loading= false;
    $scope.getEvents = function(){
        EventsFactory.getEvents($scope.data.usn);
        $scope.loading = true;
        $location.path('/events');
    }
}]);

app.controller('EventsController',['$scope', '$http','$location','EventsFactory',function($scope, $http, $location, EventsFactory){
    $scope.events = EventsFactory.events;
    $scope.usn = EventsFactory.usn;
    $scope.loading = false;
    $scope.pay = function(){
        $scope.eventsToPayFor =
        $scope.events.filter(function(event){
            return event.pay;
        }).
        map(function(event){
            return event.name;
        });

        if($scope.eventsToPayFor.length > 0){
            EventsFactory.postData = {
                usn: $scope.usn,
                events: $scope.eventsToPayFor
            };
            $scope.loading = true;
            $location.path('/receipt');
        }
        else{
            alert("No Events Selected!");
        }
    }
}]);

app.controller('ReceiptController',['$scope','EventsFactory',function($scope, EventsFactory){
    $scope.events = EventsFactory.postData.events;
}]);

app.directive('loading', function() {
    return {
        restrict: 'E',
        templateUrl: '/resources/static/templates/loading.html'
    }
});

app.directive('stopEvent', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attr) {
            element.bind('click', function (e) {
                e.stopPropagation();
            });
        }
    };
});

app.config(['$routeProvider',
        function($routeProvider) {
            $routeProvider.
            when('/', {
                templateUrl: '/resources/static/templates/get_usn.html',
                controller: 'USNController'
            }).
            when('/events',{
                templateUrl: '/resources/static/templates/show_events.html',
                controller: 'EventsController'
            }).
            when('/receipt',{
                templateUrl: '/resources/static/templates/show_receipt.html',
                controller: 'ReceiptController'
            }).
            otherwise({
                redirectTo: '/'
            });
}]);
