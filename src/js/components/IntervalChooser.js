import React, {Component, PropTypes} from "react";
import  DateTimeField from 'react-bootstrap-datetimepicker';
import moment,{Moment} from 'moment';
import FormGroup from 'react-bootstrap';
import ControlLabel from 'react-bootstrap';


export default class IntervalChooser extends Component {
    constructor(...args){
        super(...args);
    
    }
    
    
    render(){
      console.log(this.props);
      return (<div>
        
        <DateTimeField 
            dateTime = {this.props.startTime}
            onChange = {this.props.userChangedStartTime}
        />
       
        <DateTimeField 
            dateTime = {this.props.endTime}
            onChange = {this.props.userChangedEndTime}
        />
        
      </div>);  
    }
    
}



 IntervalChooser.propTypes = {
     startTime: PropTypes.string.isRequired,
     endTime: PropTypes.string.isRequired,
     userChangedStartTime: PropTypes.func.isRequired,
     userChangedEndTime: PropTypes.func.isRequired
 }