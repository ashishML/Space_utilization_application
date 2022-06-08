import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) { }
  API_ENDPOINT = environment.BASE_URL;

  UploadedVideosName = new BehaviorSubject([])
  sendExtractedData = new BehaviorSubject([])

  uploadVideo(payload:any){
    return this.http.post(`${this.API_ENDPOINT}/upload_video`, payload)
  }

  getFrames(payload:any){
    let params = new HttpParams().set("v_frames", payload);  
    return this.http.get(`${this.API_ENDPOINT}/get_frame`, {params})
  }

  sendCordinates(payload:any){
    return this.http.post(`${this.API_ENDPOINT}/roi_cordinates`, payload)
  }

  getVideos(payload:any){
    let params = new HttpParams().set("v_name", payload);    
    return this.http.get(`${this.API_ENDPOINT}/play_videos`, {params})
  }
}
