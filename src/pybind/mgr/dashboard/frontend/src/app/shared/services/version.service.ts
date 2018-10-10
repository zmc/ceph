import { HttpClient } from '@angular/common/http';
import { Injectable, NgZone } from '@angular/core';
import { Router } from '@angular/router';

import * as _ from 'lodash';
import { BehaviorSubject, Subscription } from 'rxjs';

import { ExecutingTask } from '../models/executing-task';
import { ServicesModule } from './services.module';


@Injectable({
  providedIn: ServicesModule
})
export class VersionService {
  // Observable sources
  private versionDataSource = new BehaviorSubject(null);

  // Observable streams
  versionData$ = this.versionDataSource.asObservable();

  constructor(private http: HttpClient, private router: Router, private ngZone: NgZone) {
    this.refresh();
  }
  refresh() {
    this.http.get('api/public/version').subscribe((data) => {
      this.versionDataSource.next(data);
    });

    this.ngZone.runOutsideAngular(() => {
      setTimeout(() => {
        this.ngZone.run(() => {
          this.refresh();
        });
      }, 5000);
    });
  }

}
