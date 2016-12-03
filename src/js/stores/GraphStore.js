import {Store} from "flux/utils";
import dispatcher from "../dispatcher";
import constants from "../constants";







class GraphStore extends Store {
    constructor(...args){
        super(...args);
        this.store = {
            nGraphs: 2,
            myN:4
        };
    }

    setNumGraphs(nGraphs){
        this.store.nGraphs = nGraphs;
    }

    setMyNum(myN){
        this.store.myN = myN;
    }

    getState(){
        return this.store;
    }

    __onDispatch(action){
        switch (action.type){
        case constants.SET_NUM_GRAPHS:
            this.setNumGraphs(...action.payload.args);
            this.__emitChange();
            break;
        case constants.SET_MY_NUM:
            this.setMyNum(...action.payload.args);
            this.__emitChange();
            break;
        }
        
    }


}





export default new GraphStore(dispatcher);

