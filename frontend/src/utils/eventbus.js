import cloneDeep from 'lodash/cloneDeep';

export default class EventEmitter {
    constructor() {
        this.events = {};
    }

    on(eventName, callback) {
        if(!this.events[eventName] ) {
            this.events[eventName] = [];
        }
        this.events[eventName].push(callback);
    }

    emit(eventName, data) {
        //console.log("%c+++ Event: "+eventName, "color: blue;");
        //console.log(data);
        const event = this.events[eventName];
        if(event) {
            event.forEach(callback => {
                callback.call(null, cloneDeep(data));
            });
        }
    }
}