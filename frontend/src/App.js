import React, { Component } from 'react';

import settings from './settings';


export default class App extends Component {

  constructor(props) {
    super(props);

    this.state = {
      query: {
        term: '',
        minWidth: '',
        minHeight: '',
      },
      images: [],
      isUploading: false,
    };

    // Binds for callbacks.
    this.performSearch = this.performSearch.bind(this);
    this.performUpload = this.performUpload.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleQueryChange = this.handleQueryChange.bind(this);
  }

  searchImages(query) {
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(query)
    };

    return fetch(`${settings.API_URL}/search/`, options).then(
      response => response.json()
    );
  }

  performSearch() {
    let query = {limit: 50};

    if (this.state.query.term.length > 0) {
      query.term = this.state.query.term;
    }

    if (this.state.query.minWidth.length > 0) {
      query.min_width = this.state.query.minWidth;
    }

    if (this.state.query.minHeight.length > 0) {
      query.min_height = this.state.query.minHeight;
    }

    this.searchImages(query).then(
      json => this.setState({images: json.result, totalImages: json.count})
    );
  }

  performUpload() {
    this.setState({isUploading: true});

    var data = new FormData()
    data.append('image', this.refs.fileUploader.files[0])

    fetch(`${settings.API_URL}/store/`, {
      method: 'POST',
      body: data
    }).then(
      response => {
        this.setState({isUploading: false});
        this.refs.fileUploader.value = null;  // Reset the file uploader.
      }
    );
  }

  handleQueryChange(key, value) {
    this.setState(prevState => ({query: {...prevState.query, [key]: value}}));
  }

  handleKeyDown(event) {
    if (event.key === 'Enter') {
      this.performSearch();
    }
  }

  render() {
    const images = this.state.images.map(
      image => (
        <div className="results-item" key={image.image_id}>
          <img
            alt={image.image_name}
            title={image.image_name}
            src={`http://localhost:5050/image/${image.image_id}/`}
          />
        </div>
      )
    );

    return (
      <div className="app-container">
        <div className="controls">
          <div className="search-bar">
            <input
              type="text"
              className="input-term"
              value={this.state.query.term}
              onChange={e => this.handleQueryChange('term', e.target.value)}
              onKeyDown={this.handleKeyDown}
            />
            <input
              type="text"
              className="input-width"
              value={this.state.query.minWidth}
              onChange={e => this.handleQueryChange('minWidth', e.target.value)}
              onKeyDown={this.handleKeyDown}
            />
            <input
              type="text"
              className="input-height"
              value={this.state.query.minHeight}
              onChange={e => this.handleQueryChange('minHeight', e.target.value)}
              onKeyDown={this.handleKeyDown}
            />
            <div
              className="button search-button"
              onClick={this.performSearch}
            >Search</div>
          </div>
          <div className="vertical-separator">&nbsp;</div>
          <div className="upload-bar">
            <input type="file" ref="fileUploader" />
            <div
              className="button upload-button"
              onClick={this.performUpload}
            >Upload</div>
            <div className={`spinner ${this.state.isUploading ? '' : 'hidden'}`}>...</div>
          </div>
        </div>
        <div className="separator"></div>
        <div className="results">
          {images}
        </div>
      </div>
    );
  }
}
