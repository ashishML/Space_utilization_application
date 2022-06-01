import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent implements OnInit {

  constructor(private service: ApiService) { }
  getFrame :any
  getFrameData: any;
  getFrameName: any = [];
  ngOnInit(): void {
    this.service.sendExtractedData.subscribe((res:any) => {
      console.log(res, 'frame Data');
      res.forEach((element:any) => {
        this.getFrameName.push(element.result_video_name)
      });
      this.getFrameData = res;
      console.log(this.getFrameName, 'frame name');
      this.service.getVideos(JSON.stringify(this.getFrameName)).subscribe((resp:any) => {
        console.log(resp.data);
        this.getFrame = resp.data;
      })
    })
    
  }

}
