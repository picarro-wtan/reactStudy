import dispatcher from "../dispatcher";
import constants from "../constants";

let GraphActionCreators = {
    setNumGraphs(nGraphs){
        dispatcher.dispatch({
           type: constants.SET_NUM_GRAPHS,
           payload: {nGraphs: nGraphs} //={nGraphs}
        });
    }

};
export default GraphActionCreators;
