import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import axiosInstance from "./../AxiosInstance";
import * as Y from "yjs";
import { QuillBinding } from "y-quill";
import Editor from "./../Editor/Editor";
import { useSession } from "./../ContextProviders/SessionContext";

const ORIGIN_REMOTE = "remote";

const DocumentEditor = () => {
	const { document_id } = useParams();
	const [document, setDocument] = useState(null);
	const [email, setEmail] = useState("");
	const wsRef = useRef(null);
	const documentRef = useRef(new Y.Doc());
	const quillRef = useRef();
	const { user } = useSession();

	const connect_socket = () => {
		if (wsRef.current) return;
		const ws = new WebSocket(
			`http://localhost:8000/ws/documents/${document_id}/?token=${localStorage.getItem(
				"token"
			)}`
		);
		ws.binaryType = "arraybuffer";
		wsRef.current = ws;
		ws.onopen = () => {
			console.log("socket connected");
		};
		ws.onclose = () => {
			console.log("socket disconnected");
		};

		ws.onmessage = (event) => {
			documentRef.current.transact(() => {
				const update = new Uint8Array(event.data);
				Y.applyUpdate(documentRef.current, update);
			}, ORIGIN_REMOTE);
		};
	};

	const handleInvite = async () => {
		try {
			await axiosInstance.post(`/documents/${document_id}/invite/`, {
				email,
			});
			// Refetch the document to update the collaborators list
			const response = await axiosInstance.get(`/documents/${document_id}`);
			setDocument(response.data);
			setEmail(""); // Clear the input field
		} catch (error) {
			alert("Failed to invite collaborator");
		}
	};

	const bind_document = () => {
		const handleUpdate = (update, origin) => {
			// Only send updates that originated locally
			wsRef.current.send(update);
		};

		documentRef.current.on("update", handleUpdate);

		let quill = quillRef.current;

		//Binding Quill to Yjs document
		new QuillBinding(documentRef.current.getText("content"), quill);
	};

	useEffect(() => {
		connect_socket();
		return () => {
			wsRef.current.close();
		};
	}, []);

	useEffect(() => {
		const fetchDocument = async () => {
			try {
				const response = await axiosInstance.get(`/documents/${document_id}`);
				setDocument(response.data);
			} catch (error) {
				console.error("Failed to fetch document", error);
			}
		};

		fetchDocument();
	}, [document_id]);

	if (!document) {
		return <div>Loading...</div>;
	}

	return (
		<div>
			<h2>{document.title}</h2>
			<div>
				<Editor
					ref={quillRef}
					readOnly={false}
					onReady={() => {
						bind_document();
					}}
				/>
			</div>
			<div>
				<h3>Owner</h3>
				<p>
					{document.owner.username} ({document.owner.email}){" "}
				</p>
			</div>
			<div>
				<h3>Collaborators</h3>
				<ul>
					{document.collaborators.map((collaborator) => (
						<li key={collaborator.id}>
							{collaborator.username} ({collaborator.email})
						</li>
					))}
				</ul>
				{document?.owner.id === user?.id && (
					<div>
						<h3>Invite Collaborator</h3>
						<input
							type="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							placeholder="Collaborator email"
						/>
						<button onClick={handleInvite}>Invite</button>
					</div>
				)}
			</div>
		</div>
	);
};

export default DocumentEditor;
