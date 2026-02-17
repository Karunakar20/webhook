import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
     const [events, setEvents] = useState([]);
     const [selectedEvent, setSelectedEvent] = useState(null);
     const [loading, setLoading] = useState(false);
     const [error, setError] = useState(null);

     // Fetch Events
     const fetchEvents = async () => {
          setLoading(true);
          try {
               const response = await fetch('/api/webhook/?cmd=get');
               if (!response.ok) throw new Error('Failed to fetch events');
               const data = await response.json();
               // Assuming api returns array. If it returns { events: [] }, adjust here.
               setEvents(Array.isArray(data) ? data : []);
               setError(null);
          } catch (err) {
               console.error(err);
               setError('Error fetching events. Ensure backend is running.');
          } finally {
               setLoading(false);
          }
     };

     useEffect(() => {
          fetchEvents();
          // Poll every 5 seconds to keep list updated
          const interval = setInterval(fetchEvents, 5000);
          return () => clearInterval(interval);
     }, []);

     const handleSelectEvent = async (event) => {
          // Optimistically set selected event from list first
          setSelectedEvent(event);

          // Fetch full details (if needed, e.g. if list doesn't have full payload)
          try {
               const response = await fetch(`/api/webhook/?cmd=get&id=${event.id}`);
               if (response.ok) {
                    const detailData = await response.json();
                    const freshEvent = Array.isArray(detailData) ? detailData[0] : detailData;
                    if (freshEvent) {
                         setSelectedEvent(freshEvent);
                    }
               }
          } catch (err) {
               console.error("Error fetching details", err);
          }
     };

     const handleRetry = async (id) => {
          try {
               const response = await fetch('/api/webhook/?cmd=retry_event', {
                    method: 'POST',
                    headers: {
                         'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ id: id }),
               });

               if (response.ok) {
                    alert('Retry initiated!');
                    fetchEvents(); // Refresh list immediately
                    // Also refresh selected event if it's the one we retried
                    if (selectedEvent && selectedEvent.id === id) {
                         handleSelectEvent(selectedEvent);
                    }
               } else {
                    alert('Retry failed to start.');
               }
          } catch (err) {
               console.error(err);
               alert('Error contacting server for retry.');
          }
     };

     // Create Event Logic
     const [showModal, setShowModal] = useState(false);
     const [apiKey, setApiKey] = useState('');
     const [payload, setPayload] = useState('{\n  "payload": {"id": "1", "data":"SOME"} \n}');

     const handleCreateEvent = async () => {
          try {
               // Validate JSON
               let parsedPayload;
               try {
                    parsedPayload = JSON.parse(payload);
               } catch (e) {
                    alert('Invalid JSON Payload');
                    return;
               }

               const response = await fetch('/api/webhook/?cmd=create_event', {
                    method: 'POST',
                    headers: {
                         'Content-Type': 'application/json',
                         'X-API-Key': apiKey
                    },
                    body: JSON.stringify(parsedPayload)
               });

               if (response.ok) {
                    alert('Event Created Successfully!');
                    setShowModal(false);
                    setApiKey(''); // Optional: clear or keep
                    fetchEvents();
               } else {
                    alert('Failed to create event. Check API Key.');
               }
          } catch (err) {
               console.error(err);
               alert('Error creating event.');
          }
     };

     return (
          <div className="container">
               <header>
                    <h1>Webhook Deliveries</h1>
                    <div style={{ display: 'flex', gap: '10px' }}>
                         <button onClick={fetchEvents} className="refresh-btn">Refresh</button>
                         <button onClick={() => setShowModal(true)} className="create-btn">Create Event</button>
                    </div>
               </header>
               {error && <div className="error-banner">{error}</div>}
               <main>
                    <div className="event-list">
                         <h2>Events {loading && <small>(Updating...)</small>}</h2>
                         {events.length === 0 && !loading ? <p>No events found.</p> : null}
                         <ul>
                              {events.map(event => (
                                   <li key={event.id} onClick={() => handleSelectEvent(event)} className={selectedEvent && selectedEvent.id === event.id ? 'selected' : ''}>
                                        <span className={`status-dot ${event.status ? event.status.toLowerCase() : 'unknown'}`}></span>
                                        <div className="event-info">
                                             <div className="event-name">{event.name || event.type || 'Unknown Event'}</div>
                                             <div className="event-status">{event.status || 'No Status'}</div>
                                             {/* <div className="event-time">{event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : `ID: ${event.id}`}</div> */}
                                        </div>
                                   </li>
                              ))}
                         </ul>
                    </div>
                    <div className="event-details">
                         {selectedEvent ? (
                              <div className="detail-card">
                                   <h2>Event Details</h2>
                                   <div className="detail-row">
                                        <strong>ID:</strong> {selectedEvent.id}
                                   </div>
                                   <div className="detail-row">
                                        <strong>Name:</strong> {selectedEvent.name || selectedEvent.type || 'N/A'}
                                   </div>
                                   <div className="detail-row">
                                        <strong>Status:</strong> <span className={`status-badge ${selectedEvent.status ? selectedEvent.status.toLowerCase() : ''}`}>{selectedEvent.status}</span>
                                   </div>
                                   <div className="detail-row">
                                        <strong>Attempts:</strong> {selectedEvent.attempts || 0}
                                   </div>
                                   <div className="detail-row">
                                        <strong>Url:</strong> {selectedEvent.url || ''}
                                   </div>
                                   <div className="detail-row">
                                        <strong>Payload:</strong>
                                        <pre>{JSON.stringify(selectedEvent.payload || {}, null, 2)}</pre>
                                   </div>
                                   <div className="detail-row">
                                        <strong>Meta:</strong>
                                        <pre>{JSON.stringify(selectedEvent.headers || {}, null, 2)}</pre>
                                   </div>
                                   {selectedEvent.status && selectedEvent.status.toLowerCase() === 'failed' && (
                                        <button onClick={() => handleRetry(selectedEvent.id)} className="retry-btn">
                                             Retry Event
                                        </button>
                                   )}
                              </div>
                         ) : (
                              <div className="no-selection">Select an event to view details</div>
                         )}
                    </div>
               </main>

               {showModal && (
                    <div className="modal-overlay">
                         <div className="modal-content">
                              <h2>Create New Event</h2>
                              <div className="form-group">
                                   <label>API Key (X-API-Key)</label>
                                   <input
                                        type="text"
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        placeholder="Enter Integration API Key"
                                   />
                              </div>
                              <div className="form-group">
                                   <label>JSON Payload</label>
                                   <textarea
                                        value={payload}
                                        onChange={(e) => setPayload(e.target.value)}
                                   />
                              </div>
                              <div className="modal-actions">
                                   <button onClick={() => setShowModal(false)} className="btn btn-secondary">Cancel</button>
                                   <button onClick={handleCreateEvent} className="btn btn-primary">Create</button>
                              </div>
                         </div>
                    </div>
               )}
          </div>
     );
}

export default App;
