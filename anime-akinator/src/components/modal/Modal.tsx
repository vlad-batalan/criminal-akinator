import React, { useEffect, useRef } from "react";
import { CSSTransition } from "react-transition-group";
import "./modalStyles.css";

type Listener = (this: HTMLElement, ev: KeyboardEvent) => any;

const useOnEscapeClick = (callback: () => void) => {
    useEffect(() => {
        const closeOnEscapeKey: Listener = (e) =>
            e.key === "Escape" ? callback() : null;
        document.body.addEventListener("keydown", closeOnEscapeKey);
        return () => {
            document.body.removeEventListener("keydown", closeOnEscapeKey);
        };
    }, [callback]);
};

function Modal({
    children,
    isOpen,
    handleClose
}: {
    children: React.ReactNode;
    isOpen: boolean;
    handleClose: () => void;
}) {
    useOnEscapeClick(handleClose);
    const nodeRef = useRef(null);
    return (
        <CSSTransition
            in={isOpen}
            timeout={{ exit: 300 }}
            unmountOnExit
            classNames="modal"
            nodeRef={nodeRef}
        >
        <div className="modal" ref={nodeRef}>
            <button onClick={handleClose} className="close-btn">
                Close
            </button>
            <div className="modal-content">{children}</div>
        </div> 
        </CSSTransition>
    );
}
export default Modal;