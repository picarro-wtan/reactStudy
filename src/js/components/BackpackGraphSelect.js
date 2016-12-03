import React, {Component, propTypes} from "react";
import GraphNum from "./GraphNum";
import VarChooser from "./VarChooser";
import FormGroup from 'react-bootstrap';
import ControlLabel from 'react-bootstrap';
import moment,{Moment} from 'moment';
import IntervalChooser from './IntervalChooser';
import GraphStore from '../stores/GraphStore';


export default class BackpackGraphSelect extends Component {
    constructor(...args){
      super(...args);
      //initial states
      this.state = {
                    selectedVars: ["CH4","CO2","H2O"], 
                    selectedStartTime: new Date().getTime().toString() ,  
                    selectedEndTime: new Date().getTime().toString() };
      //for any call-back func, bind this
      this.graphNumChanged = this.graphNumChanged.bind(this);
      this.selectedVarChanged = this.selectedVarChanged.bind(this);
      
      this.variables = ["CH4","CO2","H2O"];
      this.graphStoreListener = null;

    }
    
    componentWillMount(){
      this.handleGraphStoreChange();
      this.graphStoreListener = GraphStore.addListener(data => this.handleGraphStoreChange(data));
    }
    
    handleGraphStoreChange(){
      this.setState(GraphStore.getState());
    };
    
    componentWillUnmount(){
      this.graphStoreListener.remove();
    };

    render(){

      let choosers = [];  //jsx var
      let showChoosersVar = [];
      
      for (let i=0; i<this.state.nGraphs;i++){
        choosers.push(
          <VarChooser key={i} 
            graphIdx={i+1} 
            variables = {this.variables} 
            selectedVar ={this.state.selectedVars[i]} 
            userInput = {(variable) => this.selectedVarChanged(variable, i)}
          />
        );
        
        showChoosersVar.push(
          <p key={i}> Graph{i+1} value is {this.state.selectedVars[i]}</p>
        );
        
      }
      
      //var DateTimeField = require('react-bootstrap-datetimepicker');
      
      let showTimeRange = <p> Selected Time Range:<br/>   
                              {moment(+this.state.selectedStartTime).format('YYYY-MM-DD HH:mm:ss')} 
                              ------- 
                              {moment(+this.state.selectedEndTime).format('YYYY-MM-DD HH:mm:ss')} 
                          </p>;
      
      return (<div>
        <GraphNum nGraphs= {this.state.nGraphs} userInput = {this.graphNumChanged} />
        <p>Value is {this.state.nGraphs}</p>
        {choosers}
        {showChoosersVar}
        <IntervalChooser 
            startTime = {this.state.selectedStartTime} 
            endTime = {this.state.selectedEndTime}
            userChangedStartTime = {(time) => {this.setState({selectedStartTime : time})}}
            userChangedEndTime = {(time) => {this.setState({selectedEndTime : time})}}/> 
        
        <IntervalChooser 
            startTime = {this.state.selectedStartTime} 
            endTime = {this.state.selectedEndTime}
            userChangedStartTime = {(time) => {this.setState({selectedStartTime : time})}}
            userChangedEndTime = {(time) => {this.setState({selectedEndTime : time})}}/> 
        
        
        {showTimeRange}
      </div>);  
    };
    

    selectedVarChanged(variable,i){
      let selection = this.state.selectedVars.slice(0);
      selection[i] = variable;
      this.setState({selectedVars: selection});
    }
    
    graphNumChanged(x){
      this.setState({nGraphs: x})
    }
    
}