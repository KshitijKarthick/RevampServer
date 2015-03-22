var app = angular.module('RegApp',['ngRoute']);

app.factory('EventsFactory',['$http',function($http){
    var factory = {};
    factory.getEvents = function(usn){
        this.usn = usn;
        return $http.get('/eventsOf/'+usn);
    }

    factory.pay = function(index,callback){
        function payNext(){
            if(index+1 < factory.eventsToPayFor.length){
                factory.pay(index+1,callback);
            }else{
                callback();
            }
        }

        $http.post('payForEvent',{phone_num: factory.usn, event: factory.eventsToPayFor[index]['event']})
        .success(payNext)
        .error(payNext);
    }

    factory.payAllAndDo = function(callback){
        factory.pay(0,callback);
    }
    return factory;
}]);

app.controller('USNController', ['$scope', '$location', 'EventsFactory', function($scope, $location, EventsFactory){
    $scope.data ={}
    $scope.data.usn = '';
    $scope.loading= false;
    $scope.getEvents = function(){
        $scope.loading = true;
        EventsFactory
        .getEvents($scope.data.usn)
        .success(function(data){
            $scope.loading = false;
            $location.path('/events');
            EventsFactory.events = data.events;
        })
        .error(function(){
            $scope.loading = false;
            alert("Error Fetching details! Try again.");
        });
    }
}]);

app.controller('EventsController',['$scope', '$http','$location','EventsFactory',function($scope, $http, $location, EventsFactory){
    $scope.events = EventsFactory.events;
    $scope.usn = EventsFactory.usn;
    $scope.loading = false;
    $scope.pay = function(){
        EventsFactory.eventsToPayFor =
            $scope.events.filter(function(event){
            return event.pay;
        });

        if(EventsFactory.eventsToPayFor.length > 0){
            $scope.loading = true;
            EventsFactory.payAllAndDo(function(){
                $scope.loading = false;
                $location.path('/receipt');
            });
        }
        else{
            alert("No Events Selected!");
        }
    }
}]);

app.controller('ReceiptController',['$scope','EventsFactory',function($scope, EventsFactory){
    $scope.events = EventsFactory.eventsToPayFor;
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
