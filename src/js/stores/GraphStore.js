import {Store} from "flux/utils";
import dispatcher from "../dispatcher";
import constants from "../constants";







class GraphStore extends Store {
    constructor(...args){
        super(...args);
        this.store = {
            nGraphs: 2
        };
    }

    setNumGraphs(nGraphs){
        this.store.nGraphs = nGraphs;
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
        }
        
    }


}





export default new GraphStore(dispatcher);

