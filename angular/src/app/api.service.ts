import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) { }
  API_ENDPOINT = environment.BASE_URL;

  uploadVideo(payload:any){
    return this.http.post(`${this.API_ENDPOINT}/upload_video`, payload)
  }

  getNames(payload:any){
    return this.http.get(`${this.API_ENDPOINT}/get_names`, payload)
  }

  getFrames(){
    return this.http.get(`${this.API_ENDPOINT}/get_frame`)
  }
}
