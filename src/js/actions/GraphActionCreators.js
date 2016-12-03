import dispatcher from "../dispatcher";
import constants from "../constants";

let GraphActionCreators = {
    setNumGraphs(...args){
        dispatcher.dispatch({
           type: constants.SET_NUM_GRAPHS,
           payload: {args} 
        });
    }
};



export default GraphActionCreators;
