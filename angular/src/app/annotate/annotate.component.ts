import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-annotate',
  templateUrl: './annotate.component.html',
  styleUrls: ['./annotate.component.css']
})
export class AnnotateComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }
  context: any = [];
  current_image_loaded: any = [];
  img_index: any;
  img_org_height: any = [];
  img_element = [];
  img_org_width: any = [];
  image_panel_width: any = [];
  image_panel_height: any = [];
  region_canvas_element: any = [];
  _canvas_scale: any = [];
  annotationInfoExists: any = [];
  all_points_x: any = [];
  all_points_y: any = [];
  REGION_SHAPES_POINTS_RADIUS: number = 3;
  THEME_SEL_REGION_FILL_BOUNDARY_COLOR: any = "yellow";
  THEME_CONTROL_POINT_COLOR: any = '#ff0000';
  highlighted: boolean = false;
  changeCursor!: boolean;
  THEME_REGION_BOUNDARY_WIDTH: number = 3;
  scaling: any = [];
  poly_region_edge: any;
  POLYGON_VERTEX_MATCH_TOL: number = 5;
  is_user_resizing_region: any;
  POLYGON_RESIZE_VERTEX_OFFSET: number = 100;
  _via_current_x: any;
  _via_current_y: any;
  image_points_x: any = [];
  image_points_y: any = [];
  updatedImages = new Set();

  afterLoading() {
    //console.log("in afterloading function:",this.loaded)
    if (!this.current_image_loaded[this.img_index]) {

      // this.img_org_height[this.img_index] = this.img_element[this.img_index].naturalHeight;
      // this.img_org_width[this.img_index] = this.img_element[this.img_index].naturalWidth;
      //console.log("region_canvas_element:",this.region_canvas_element[this.img_index], "org width", img_org_width)
      this.image_panel_width[this.img_index] = 446;
      this.image_panel_height[this.img_index] = 334;
      this.region_canvas_element[this.img_index].width = this.img_org_width[this.img_index];
      this.region_canvas_element[this.img_index].height = this.img_org_height[this.img_index];
      let _img_canvas_width = this.region_canvas_element[this.img_index].width;
      let _img_canvas_height = this.region_canvas_element[this.img_index].height;

      if (_img_canvas_width > this.image_panel_width[this.img_index]) {
        // resize image to match the panel width
        let scale_width = this.image_panel_width[this.img_index] / this.img_org_width[this.img_index];
        _img_canvas_width = this.image_panel_width[this.img_index];
        _img_canvas_height = this.img_org_height[this.img_index] * scale_width;
      }
      else {
        this.image_panel_width[this.img_index] = _img_canvas_width;
      }
      if (_img_canvas_height > this.image_panel_height[this.img_index]) {
        // resize further image if its height is larger than the image panel
        var scale_height = this.image_panel_height[this.img_index] / _img_canvas_height;
        _img_canvas_height = this.image_panel_height[this.img_index];
        _img_canvas_width = _img_canvas_width * scale_height;
      } else {
        this.image_panel_height[this.img_index] = _img_canvas_height;
      }
      _img_canvas_width = Math.round(_img_canvas_width);
      _img_canvas_height = Math.round(_img_canvas_height);
      this._canvas_scale[this.img_index] = this.img_org_width[this.img_index] / _img_canvas_width;
      this.region_canvas_element[this.img_index].width = _img_canvas_width;
      this.region_canvas_element[this.img_index].height = _img_canvas_height;
      //draw image in canvas after re-sizing the height and width 
      this.context[this.img_index].drawImage(this.img_element[this.img_index], 0, 0, this.img_org_width[this.img_index], this.img_org_height[this.img_index], 0, 0, this.image_panel_width[this.img_index], this.image_panel_height[this.img_index]);
      //only if the annotation exists(i.e co-ordinates are present in the <video_name>_damage.json file)
      if (this.annotationInfoExists[this.img_index]) {
        if (this.scaling[this.img_index]) {
          for (var j = 0; j < this.all_points_x[this.img_index].length; ++j) {
            this.all_points_x[this.img_index][j] = Math.round(this.all_points_x[this.img_index][j] / this._canvas_scale[this.img_index]);
            this.all_points_y[this.img_index][j] = Math.round(this.all_points_y[this.img_index][j] / this._canvas_scale[this.img_index]);
          }
          this.scaling[this.img_index] = false;
        }
        this.drawPolygonShape();
      }
      this.current_image_loaded[this.img_index] = true;
    }

  }

  drawPolygonShape() {
    this.context[this.img_index].strokeStyle = this.THEME_SEL_REGION_FILL_BOUNDARY_COLOR;
    this.context[this.img_index].lineWidth = this.THEME_REGION_BOUNDARY_WIDTH / 2;
    this.context[this.img_index].beginPath();
    let all_points_x = this.all_points_x[this.img_index];
    let all_points_y = this.all_points_y[this.img_index];
    this.context[this.img_index].moveTo(all_points_x[0], all_points_y[0]);
    for (var i = 1; i < this.all_points_x[this.img_index].length; ++i) {
      this.context[this.img_index].lineTo(all_points_x[i], all_points_y[i]);
    }
    this.context[this.img_index].lineTo(all_points_x[0], all_points_y[0]); // close loop

    this.context[this.img_index].stroke();
  }

  highlight() {
    if (!this.highlighted) {
      this.drawPolygonShape();
      let all_points_x = this.all_points_x[this.img_index];
      let all_points_y = this.all_points_y[this.img_index];
      this.context[this.img_index].globalAlpha = 1.0;
      for (var i = 0; i < all_points_x.length; ++i) {
        this.drawControlPoint(all_points_x[i], all_points_y[i]);
      }
      this.changeCursor = true;
    }
    else {
      // this.highlighted = false;

    }
  }

  drawControlPoint(cx:any, cy:any) {
    this.context[this.img_index].beginPath();
    this.context[this.img_index].arc(cx, cy, this.REGION_SHAPES_POINTS_RADIUS, 0, 2 * Math.PI, false);
    this.context[this.img_index].closePath();

    this.context[this.img_index].fillStyle = this.THEME_CONTROL_POINT_COLOR;
    this.context[this.img_index].globalAlpha = 1.0;
    this.context[this.img_index].fill();
  }

  onMouseDown(e:any) {
    //console.log("mouse down")
    e.stopPropagation();

    //let _via_click_x0 = e.offsetX; let _via_click_y0 = e.offsetY;
    this.poly_region_edge = this.is_on_region_corner(e.offsetX, e.offsetY);
    if (this.changeCursor) {
      // check if user clicked on the region boundary
      if (this.poly_region_edge[1] > 0) {
        if (!this.is_user_resizing_region) {
          // resize region
          this.is_user_resizing_region = true;
        }
        else {
          this.is_user_resizing_region = false;
        }
      } else {
        this.is_user_resizing_region = false;
      }
    }
  }

  is_on_region_corner(px: any, py: any): any {
    let poly_region_edge = [-1, -1];
    let result = this.is_on_polygon_vertex(this.all_points_x[this.img_index],
      this.all_points_y[this.img_index],
      px, py);

    if (result > 0) {
      poly_region_edge[1] = result;
      //console.log("resizing edge value", poly_region_edge)
      return poly_region_edge;
    }
    return poly_region_edge;
  }
  is_on_polygon_vertex(all_points_x: any, all_points_y: any, px: any, py: any) {
    let i, n;
    n = all_points_x.length;

    for (i = 0; i < n; ++i) {
      if (Math.abs(all_points_x[i] - px) < this.POLYGON_VERTEX_MATCH_TOL &&
        Math.abs(all_points_y[i] - py) < this.POLYGON_VERTEX_MATCH_TOL) {
        return (this.POLYGON_RESIZE_VERTEX_OFFSET + i);
      }
    }
    return 0;
  }

  onMouseMove(e:any) {
    //e.preventDefault()
    //console.log("mouse move");
    this._via_current_x = e.offsetX; this._via_current_y = e.offsetY;
    if (!this.is_user_resizing_region) {
      this.poly_region_edge = this.is_on_region_corner(this._via_current_x, this._via_current_y);
    }
    if (this.changeCursor && this.is_user_resizing_region) {
      //redraw
      this.context[this.img_index].clearRect(0, 0, this.region_canvas_element[this.img_index].width, this.region_canvas_element[this.img_index].height);
      this.context[this.img_index].drawImage(this.img_element[this.img_index], 0, 0, this.img_org_width[this.img_index], this.img_org_height[this.img_index], 0, 0, this.image_panel_width[this.img_index], this.image_panel_height[this.img_index]);
      this.region_canvas_element[this.img_index].focus();
      
      this.drawPolygonRegionAsUserResizes(this.all_points_x[this.img_index],
        this.all_points_y[this.img_index],
        true,
        'polygon');
      
      var moved_all_points_x = this.all_points_x[this.img_index].slice(0);
      var moved_all_points_y = this.all_points_y[this.img_index].slice(0);
      var moved_vertex_id = this.poly_region_edge[1] - this.POLYGON_RESIZE_VERTEX_OFFSET;

      moved_all_points_x[moved_vertex_id] = this._via_current_x;
      moved_all_points_y[moved_vertex_id] = this._via_current_y;

      this.drawPolygonRegionAsUserResizes(moved_all_points_x,  moved_all_points_y,   true,  "polygon");

    }
  }

  drawPolygonRegionAsUserResizes(moved_all_points_x: any, moved_all_points_y: any, arg2: boolean, arg3: string) {
    
    this.context[this.img_index].strokeStyle = this.THEME_SEL_REGION_FILL_BOUNDARY_COLOR;
    this.context[this.img_index].lineWidth = this.THEME_REGION_BOUNDARY_WIDTH / 2;
    this.context[this.img_index].beginPath();
    let all_points_x = moved_all_points_x;
    let all_points_y = moved_all_points_y
    this.context[this.img_index].moveTo(all_points_x[0], all_points_y[0]);
    for (var i = 1; i < this.all_points_x[this.img_index].length; ++i) {
      this.context[this.img_index].lineTo(all_points_x[i], all_points_y[i]);
    }
    
    this.context[this.img_index].lineTo(all_points_x[0], all_points_y[0]); // close loop
  
    this.context[this.img_index].stroke();

    //this.context[this.img_index].fillStyle   = this.VIA_THEME_SEL_REGION_FILL_COLOR;
    //this.context[this.img_index].globalAlpha = this.VIA_THEME_SEL_REGION_OPACITY;
    //this.context[this.img_index].fill();
    this.context[this.img_index].globalAlpha = 1.0;
    for (var i = 0; i < all_points_x.length; ++i) {
      this.drawControlPoint(all_points_x[i], all_points_y[i]);
    }

  }

  onMouseUp(e:any) {
    e.stopPropagation();
    let i = this.img_element.every((val:any) => val === this.img_element[0]);

    // indicates that user has finished resizing a region
    if (this.is_user_resizing_region) {
      this.is_user_resizing_region = false;
      var moved_vertex_id = this.poly_region_edge[1] - this.POLYGON_RESIZE_VERTEX_OFFSET;
      //console.log("mouse up moved vertex:", moved_vertex_id, "updated points y:", this.image_points_y)
      // update coordinate of vertex
      var imx = Math.round(this._via_current_x * this._canvas_scale[this.img_index]);
      var imy = Math.round(this._via_current_y * this._canvas_scale[this.img_index]);
      this.image_points_x[this.img_index][moved_vertex_id] = imx;
      this.image_points_y[this.img_index][moved_vertex_id] = imy;
      this.all_points_x[this.img_index][moved_vertex_id] = Math.round(imx / this._canvas_scale[this.img_index]);
      this.all_points_y[this.img_index][moved_vertex_id] = Math.round(imy / this._canvas_scale[this.img_index]);

      //clear and redraw image as user resizes the polygon shape
      this.context[this.img_index].clearRect(0, 0, this.region_canvas_element[this.img_index].width, this.region_canvas_element[this.img_index].height);
      this.context[this.img_index].drawImage(this.img_element[this.img_index], 0, 0, this.img_org_width[this.img_index], this.img_org_height[this.img_index], 0, 0, this.image_panel_width[this.img_index], this.image_panel_height[this.img_index]);

      //add the updated images index
      this.updatedImages.add(this.img_index);
      //console.log("image updated", this.updatedImages)
      this.drawPolygonRegionAsUserResizes(this.all_points_x[this.img_index], this.all_points_y[this.img_index], true, 'polygon');
      this.region_canvas_element[this.img_index].focus();
    }
  }

  onMouseOver(e:any) {

  }

}
