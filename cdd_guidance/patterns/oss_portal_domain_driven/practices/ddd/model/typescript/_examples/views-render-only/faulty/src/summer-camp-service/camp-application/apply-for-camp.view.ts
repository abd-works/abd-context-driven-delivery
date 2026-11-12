import { Component } from '@angular/core';
@Component({ selector: 'apply-for-camp', template: '<gds-button>Apply</gds-button>' })
export class ApplyForCampView {
  async ngOnInit() { this.seats = await fetch('/bff/camp-applications/seats'); }
}
